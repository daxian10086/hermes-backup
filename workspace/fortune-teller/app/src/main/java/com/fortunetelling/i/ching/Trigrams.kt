package com.fortunetelling.i.ching

object Trigrams {
    val QIAN = Trigram("乾", "☰", 7, "天")
    val DUI = Trigram("兑", "☱", 2, "泽")
    val LI = Trigram("离", "☲", 3, "火")
    val ZHEN = Trigram("震", "☳", 4, "雷")
    val XUN = Trigram("巽", "☴", 5, "风")
    val KAN = Trigram("坎", "☵", 6, "水")
    val GEN = Trigram("艮", "☶", 1, "山")
    val KUN = Trigram("坤", "☷", 0, "地")

    fun getByBinary(binary: Int): Trigram {
        return when (binary) {
            0 -> KUN
            1 -> GEN
            2 -> DUI
            3 -> LI
            4 -> ZHEN
            5 -> XUN
            6 -> KAN
            7 -> QIAN
            else -> KUN
        }
    }
}
