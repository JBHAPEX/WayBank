// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@uniswap/v3-periphery/contracts/interfaces/INonfungiblePositionManager.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

interface IDerivatives {
    function hedge(bool isLong, uint256 amount, uint256 price) external returns (uint256);
}

contract MultiPoolBalancer is Ownable, Pausable {

    struct PoolInfo {
        IERC20 token0;
        IERC20 token1;
        uint24 fee;
        int24 tickLower;
        int24 tickUpper;
        uint256 lowerRange;
        uint256 upperRange;
        address derivativesContract;
        AggregatorV3Interface priceOracle;
        bool active;
    }

    INonfungiblePositionManager public positionManager;
    PoolInfo[] public pools;

    event PoolAdded(uint256 indexed poolId);
    event RangeAdjusted(uint256 indexed poolId, uint256 newLower, uint256 newUpper);
    event HedgeExecuted(uint256 indexed poolId, string action, uint256 positionId);

    constructor(address _positionManager) Ownable(msg.sender) {
        positionManager = INonfungiblePositionManager(_positionManager);
    }

    function addPool(
        address token0, address token1, uint24 fee, int24 tickLower, int24 tickUpper,
        uint256 lowerRange, uint256 upperRange, address derivativesContract, address priceOracle
    ) external onlyOwner {
        pools.push(PoolInfo({
            token0: IERC20(token0),
            token1: IERC20(token1),
            fee: fee,
            tickLower: tickLower,
            tickUpper: tickUpper,
            lowerRange: lowerRange,
            upperRange: upperRange,
            derivativesContract: derivativesContract,
            priceOracle: AggregatorV3Interface(priceOracle),
            active: true
        }));
        emit PoolAdded(pools.length - 1);
    }

    function executeStrategy(uint256 poolId, uint256 amountToHedge) external onlyOwner whenNotPaused {
        PoolInfo storage pool = pools[poolId];
        require(pool.active, "Pool not active");

        (, int256 price, , , ) = pool.priceOracle.latestRoundData();
        require(price > 0, "Invalid price from oracle");
        uint256 currentPrice = uint256(price);

        if (currentPrice > pool.upperRange) {
            uint256 positionId = IDerivatives(pool.derivativesContract).hedge(false, amountToHedge, currentPrice);
            emit HedgeExecuted(poolId, "Short Hedge Executed", positionId);
            adjustLiquidityRange(poolId, pool.upperRange, pool.upperRange + (pool.upperRange - pool.lowerRange));
        } else if (currentPrice < pool.lowerRange) {
            uint256 positionId = IDerivatives(pool.derivativesContract).hedge(true, amountToHedge, currentPrice);
            emit HedgeExecuted(poolId, "Long Hedge Executed", positionId);
            adjustLiquidityRange(poolId, pool.lowerRange - (pool.upperRange - pool.lowerRange), pool.lowerRange);
        } else {
            emit HedgeExecuted(poolId, "Price within range, no action", 0);
        }
    }

    function adjustLiquidityRange(uint256 poolId, uint256 newLower, uint256 newUpper) internal {
        PoolInfo storage pool = pools[poolId];
        require(newLower < newUpper, "Invalid range");
        pool.lowerRange = newLower;
        pool.upperRange = newUpper;
        emit RangeAdjusted(poolId, newLower, newUpper);
    }

    function setPoolActive(uint256 poolId, bool active) external onlyOwner {
        pools[poolId].active = active;
    }

    function pause() external onlyOwner {
        _pause();
    }

    function unpause() external onlyOwner {
        _unpause();
    }

    function getPool(uint256 poolId) external view returns (PoolInfo memory) {
        return pools[poolId];
    }

    function getPoolsCount() external view returns (uint256) {
        return pools.length;
    }
}