package com.fortunetelling.i.ching

import kotlin.random.Random

object HexagramGenerator {
    var currentHexagram: Hexagram? = null

    fun randomHexagram(): Hexagram {
        // 随机生成上卦和下卦
        val upperBinary = Random.nextInt(0, 8)  // 0-7
        val lowerBinary = Random.nextInt(0, 8)  // 0-7

        val upperTrigram = Trigrams.getByBinary(upperBinary)
        val lowerTrigram = Trigrams.getByBinary(lowerBinary)

        // 根据上下卦确定卦序
        val hexagramNumber = calculateHexagramNumber(upperBinary, lowerBinary)

        val hexagram = HexagramsData.getHexagram(hexagramNumber)
        currentHexagram = hexagram
        return hexagram
    }

    private fun calculateHexagramNumber(upper: Int, lower: Int): Int {
        // 上下卦二进制组合得到卦序 (参考易经排列)
        // 这是简化版，实际64卦有固定顺序
        val hexagramIndex = upper * 8 + lower + 1
        return if (hexagramIndex > 64) hexagramIndex - 64 else hexagramIndex
    }
}
