// 核心逻辑：摇一摇算卦 + 震动反馈 + 分享解锁

package com.fortunetelling.i.ching

import android.animation.AnimatorSet
import android.animation.ObjectAnimator
import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.Vibrator
import android.view.View
import android.view.animation.AccelerateDecelerateInterpolator
import android.view.animation.AlphaAnimation
import android.view.MenuItem
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.cardview.widget.CardView
import com.google.android.material.button.MaterialButton
import kotlin.random.Random

class MainActivity : AppCompatActivity(), SensorEventListener {

    // 原有控件
    private lateinit var btnCastHexagram: MaterialButton
    private lateinit var cardResult: CardView
    private lateinit var tvHexagramNumber: TextView
    private lateinit var tvHexagramName: TextView
    private lateinit var tvSelectedLineName: TextView
    private lateinit var tvUpperTrigram: TextView
    private lateinit var tvLowerTrigram: TextView
    private lateinit var tvOverallMeaning: TextView
    private lateinit var layoutLines: LinearLayout
    private lateinit var tvSelectedLine: TextView
    private lateinit var tvShaking: TextView
    private lateinit var ivShaking: ImageView
    private lateinit var ivStickOut: ImageView
    private lateinit var layoutShaking: FrameLayout
    private lateinit var layoutTitle: LinearLayout

    // 选项页
    private lateinit var tabLines: TextView
    private lateinit var tabSelected: TextView
    private lateinit var tabFortune: TextView
    private lateinit var pageLines: LinearLayout
    private lateinit var pageSelected: LinearLayout
    private lateinit var pageFortune: LinearLayout
    private lateinit var scrollView: ScrollView

    // 运势卡片
    private lateinit var tvLoveContent: TextView
    private lateinit var tvCareerContent: TextView
    private lateinit var tvWealthContent: TextView
    private lateinit var tvHealthContent: TextView
    private lateinit var tvFamilyContent: TextView
    private lateinit var tvRelationContent: TextView
    private lateinit var tvStockContent: TextView

    // 新增：摇一摇相关
    private var sensorManager: SensorManager? = null
    private var accelerometer: Sensor? = null

    // 新增：震动
    private var vibrator: Vibrator? = null
    private var isVibrating = false
    private var vibrationRunnable: Runnable? = null
    private var vibrationHandler: Handler? = null

    // 新增：状态管理
    private var isAnimating = false
    private var isShaking = false
    private var hasShared = false
    private var currentTab = 0 // 0=运势详解, 1=选中爻, 2=其他爻
    private var currentHexagram: Hexagram? = null
    private var currentLineIndex: Int = 0
    private var adCountdownHandler: Handler? = null

    // 摇一摇检测变量
    private var lastX = 0f
    private var lastY = 0f
    private var lastZ = 0f
    private var lastShakeTime = 0L
    private var shakeStartTime = 0L
    private val SHAKE_THRESHOLD = 12f // 摇动阈值（加速度变化量）
    private val SHAKE_INTERVAL = 100L // 摇动检测间隔（毫秒）
    private val SHAKE_STOP_TIMEOUT = 800L // 800ms无摇动视为停止
    private val VIBRATION_INTERVAL = 80L // 震动间隔（毫秒）

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        try {
            setContentView(R.layout.activity_main)
            initViews()
            setupClickListeners()
            initSensors()
            loadShareState()
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun initViews() {
        btnCastHexagram = findViewById(R.id.btnCastHexagram)
        cardResult = findViewById(R.id.cardResult)
        tvHexagramNumber = findViewById(R.id.tvHexagramNumber)
        tvHexagramName = findViewById(R.id.tvHexagramName)
        tvSelectedLineName = findViewById(R.id.tvSelectedLineName)
        tvUpperTrigram = findViewById(R.id.tvUpperTrigram)
        tvLowerTrigram = findViewById(R.id.tvLowerTrigram)
        tvOverallMeaning = findViewById(R.id.tvOverallMeaning)
        layoutLines = findViewById(R.id.layoutLines)
        tvSelectedLine = findViewById(R.id.tvSelectedLine)
        tvShaking = findViewById(R.id.tvShaking)
        ivShaking = findViewById(R.id.ivShaking)
        ivStickOut = findViewById(R.id.ivStickOut)
        layoutShaking = findViewById(R.id.layoutShaking)
        layoutTitle = findViewById(R.id.layoutTitle)

        // 选项页
        tabLines = findViewById(R.id.tabLines)
        tabSelected = findViewById(R.id.tabSelected)
        tabFortune = findViewById(R.id.tabFortune)
        pageLines = findViewById(R.id.pageLines)
        pageSelected = findViewById(R.id.pageSelected)
        pageFortune = findViewById(R.id.pageFortune)
        scrollView = findViewById(R.id.scrollView)

        // 运势内容
        tvLoveContent = findViewById(R.id.tvLoveContent)
        tvCareerContent = findViewById(R.id.tvCareerContent)
        tvWealthContent = findViewById(R.id.tvWealthContent)
        tvHealthContent = findViewById(R.id.tvHealthContent)
        tvFamilyContent = findViewById(R.id.tvFamilyContent)
        tvRelationContent = findViewById(R.id.tvRelationContent)
        tvStockContent = findViewById(R.id.tvStockContent)

        // Toolbar
        val toolbar = findViewById<androidx.appcompat.widget.Toolbar>(R.id.toolbar)
        setSupportActionBar(toolbar)

    }

    private fun setupClickListeners() {
        btnCastHexagram.setOnClickListener {
            if (!isAnimating && !isShaking) {
                startShakeProcess()
            }
        }

        // 选项页切换
        tabFortune.setOnClickListener { switchTab(0) }
        tabSelected.setOnClickListener { switchTab(1) }
        tabLines.setOnClickListener { switchTab(2) }

        // 设置运势卡片点击折叠/展开
        setupFoldableCard(R.id.cardLove, R.id.tvLoveTitle, R.id.tvLoveContent)
        setupFoldableCard(R.id.cardCareer, R.id.tvCareerTitle, R.id.tvCareerContent)
        setupFoldableCard(R.id.cardWealth, R.id.tvWealthTitle, R.id.tvWealthContent)
        setupFoldableCard(R.id.cardHealth, R.id.tvHealthTitle, R.id.tvHealthContent)
        setupFoldableCard(R.id.cardFamily, R.id.tvFamilyTitle, R.id.tvFamilyContent)
        setupFoldableCard(R.id.cardRelation, R.id.tvRelationTitle, R.id.tvRelationContent)
        setupFoldableCard(R.id.cardStock, R.id.tvStockTitle, R.id.tvStockContent)
        
        // 默认显示运势详解
        switchTab(0)
    }

    private fun initSensors() {
        // 初始化传感器
        sensorManager = getSystemService(Context.SENSOR_SERVICE) as SensorManager
        accelerometer = sensorManager?.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)

        // 初始化震动
        vibrator = getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
        vibrationHandler = Handler(Looper.getMainLooper())
        adCountdownHandler = Handler(Looper.getMainLooper())
    }

    override fun onDestroy() {
        super.onDestroy()
        // 停止传感器
        sensorManager?.unregisterListener(this)
        // 停止震动
        stopVibration()
        // 停止广告倒计时
        adCountdownHandler?.removeCallbacksAndMessages(null)
    }

    override fun onSensorChanged(event: SensorEvent?) {
        val now = System.currentTimeMillis()
        
        // 避免过于频繁的检测
        if (now - lastShakeTime < SHAKE_INTERVAL) {
            return
        }

        if (event != null) {
            val x = event.values[0]
            val y = event.values[1]
            val z = event.values[2]

            // 计算加速度变化量（欧几里得距离）
            val deltaX = kotlin.math.abs(x - lastX)
            val deltaY = kotlin.math.abs(y - lastY)
            val deltaZ = kotlin.math.abs(z - lastZ)
            val acceleration = kotlin.math.sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ)

            // 更新上次的值
            lastX = x
            lastY = y
            lastZ = z
            lastShakeTime = now

            // 检测是否摇动
            if (acceleration > SHAKE_THRESHOLD) {
                onShakeDetected(now)
            } else if (isShaking && now - shakeStartTime > SHAKE_STOP_TIMEOUT) {
                // 800ms内无摇动视为停止
                onShakeStopped()
            }
        }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {
        // 不需要处理
    }

    // 检测到摇动
    private fun onShakeDetected(now: Long) {
        if (!isShaking) {
            isShaking = true
            shakeStartTime = now

            // 开始持续震动
            startVibration()

            // 更新UI：显示正在摇卦
            showShakingState(true)

            // 开始摇签筒左右摇摆动画
            startShakeTubeAnimation()
        }
    }

    // 摇动停止
    private fun onShakeStopped() {
        if (!isShaking) return
        
        isShaking = false

        // 停止震动
        stopVibration()

        // 停止摇签筒动画
        ivShaking.clearAnimation()

        // 更新UI：显示算卦中
        showShakingState(false)

        // 停止传感器监听
        sensorManager?.unregisterListener(this)

        // 2秒后显示结果
        Handler(Looper.getMainLooper()).postDelayed({
            performCastHexagram()
        }, 2000)
    }

    // 开始摇签筒左右摇摆动画
    private fun startShakeTubeAnimation() {
        val shakeLeft = ObjectAnimator.ofFloat(ivShaking, "rotation", 0f, -15f)
        shakeLeft.duration = 150
        shakeLeft.repeatCount = ObjectAnimator.INFINITE
        shakeLeft.repeatMode = ObjectAnimator.REVERSE
        
        val shakeRight = ObjectAnimator.ofFloat(ivShaking, "rotation", 0f, 15f)
        shakeRight.duration = 150
        shakeRight.repeatCount = ObjectAnimator.INFINITE
        shakeRight.repeatMode = ObjectAnimator.REVERSE
        
        val animatorSet = AnimatorSet()
        animatorSet.playSequentially(shakeLeft, shakeRight)
        animatorSet.start()
    }

    // 开始持续震动
    private fun startVibration() {
        if (isVibrating) return
        isVibrating = true

        // 立即震动一次
        vibrator?.vibrate(50)

        // 定时震动
        vibrationRunnable = object : Runnable {
            override fun run() {
                if (isVibrating) {
                    vibrator?.vibrate(50)
                    vibrationHandler?.postDelayed(this, VIBRATION_INTERVAL)
                }
            }
        }
        vibrationHandler?.postDelayed(vibrationRunnable!!, VIBRATION_INTERVAL)
    }

    // 停止震动
    private fun stopVibration() {
        isVibrating = false
        vibrationRunnable?.let {
            vibrationHandler?.removeCallbacks(it)
        }
        vibrator?.cancel()
    }

    // 开始摇一摇流程
    private fun startShakeProcess() {
        // 隐藏之前的结果
        cardResult.visibility = View.GONE
        
        // 显示摇动提示
        showShakeHint(true)

        // 开始监听加速度
        sensorManager?.registerListener(
            this,
            accelerometer,
            SensorManager.SENSOR_DELAY_GAME
        )

        // 重置变量
        lastX = 0f
        lastY = 0f
        lastZ = 0f
        lastShakeTime = 0
        shakeStartTime = 0
        isShaking = false

        // 8秒后如果还没摇动，自动开始
        Handler(Looper.getMainLooper()).postDelayed({
            if (!isShaking && !isAnimating && btnCastHexagram.isEnabled) {
                // 8秒未摇动，自动开始
                stopAccelerometer()
                showShakingAnimation()
            }
        }, 8000)
    }

    // 显示/隐藏摇动提示
    private fun showShakeHint(show: Boolean) {
        tvShaking.visibility = if (show) View.VISIBLE else View.GONE
        if (show) {
            tvShaking.text = "📱 摇动手机开始算卦\n或等待8秒自动开始"
        }
    }

    // 更新摇动状态UI
    private fun showShakingState(shaking: Boolean) {
        if (shaking) {
            tvShaking.text = "正在摇卦..."
        } else {
            tvShaking.text = "算卦中..."
        }
    }

    // 停止加速度监听
    private fun stopAccelerometer() {
        sensorManager?.unregisterListener(this)
    }

    // 显示摇卦动画
    private fun showShakingAnimation() {
        isAnimating = true
        btnCastHexagram.isEnabled = false
        
        // 隐藏之前的结果
        cardResult.visibility = View.GONE
        
        // 恢复摇卦动画区域高度
        layoutShaking.layoutParams.height = FrameLayout.LayoutParams.WRAP_CONTENT
        layoutShaking.requestLayout()
        
        // 显示摇卦提示
        showShakeHint(false)
        
        // 显示摇卦动画区域
        tvShaking.visibility = View.VISIBLE
        ivShaking.visibility = View.VISIBLE
        tvShaking.text = "算卦中..."
        
        // 摇晃动画 - 左右摇摆
        val shakeLeft = ObjectAnimator.ofFloat(ivShaking, "rotation", 0f, -15f)
        shakeLeft.duration = 200
        shakeLeft.repeatCount = 5
        shakeLeft.repeatMode = ObjectAnimator.REVERSE
        
        val shakeRight = ObjectAnimator.ofFloat(ivShaking, "rotation", 0f, 15f)
        shakeRight.duration = 200
        shakeRight.repeatCount = 5
        shakeRight.repeatMode = ObjectAnimator.REVERSE
        
        val animatorSet = AnimatorSet()
        animatorSet.playSequentially(shakeLeft, shakeRight)
        animatorSet.duration = 2000
        animatorSet.interpolator = AccelerateDecelerateInterpolator()
        
        animatorSet.addListener(object : android.animation.Animator.AnimatorListener {
            override fun onAnimationStart(animation: android.animation.Animator) {}
            override fun onAnimationEnd(animation: android.animation.Animator) {
                Handler(Looper.getMainLooper()).postDelayed({
                    performCastHexagram()
                }, 500)
            }
            override fun onAnimationCancel(animation: android.animation.Animator) {}
            override fun onAnimationRepeat(animation: android.animation.Animator) {}
        })
        
        animatorSet.start()
        
        // 文字闪烁效果
        val blinkAnimator = AlphaAnimation(1f, 0.3f).apply {
            duration = 200
            repeatMode = android.view.animation.Animation.REVERSE
            repeatCount = 10
        }
        tvShaking.startAnimation(blinkAnimator)
    }

    // 执行算卦逻辑
    private fun performCastHexagram() {
        try {
            // 隐藏摇卦提示
            tvShaking.visibility = View.GONE
            ivShaking.visibility = View.GONE
            tvShaking.clearAnimation()
            
            // 缩回摇卦动画区域
            layoutShaking.layoutParams.height = 0
            layoutShaking.requestLayout()
            
            // 随机生成卦象
            val hexagram = HexagramGenerator.randomHexagram()
            currentHexagram = hexagram

            // 随机选择六爻中的一爻
            val lineIndex = Random.nextInt(6)
            currentLineIndex = lineIndex
            val lineNames = arrayOf("初爻", "二爻", "三爻", "四爻", "五爻", "上爻")
            val selectedLineName = lineNames[lineIndex]
            val selectedLineText = hexagram.lines[lineIndex]
            val selectedLineDesc = hexagram.lineDescriptions[lineIndex]
            
            // 重置 hasShared 状态
            hasShared = getSharedState()

            // 显示结果
            displayHexagram(hexagram, selectedLineName, selectedLineText, selectedLineDesc)

            isAnimating = false
            btnCastHexagram.isEnabled = true
        } catch (e: Exception) {
            e.printStackTrace()
            isAnimating = false
            btnCastHexagram.isEnabled = true
            AlertDialog.Builder(this)
                .setTitle("错误")
                .setMessage("算卦出错：${e.message}")
                .setPositiveButton("确定", null)
                .show()
        }
    }

    // 显示结果
    private fun displayHexagram(hexagram: Hexagram, selectedLineName: String, selectedLineText: String, selectedLineDesc: String) {
        // 更新卦象信息 - UI布局优化（v2.3.4）
        // 左边：第X卦（灰色小字）+ 卦名（黑色大字）+ 爻位（红色）
        tvHexagramNumber.text = "第${hexagram.number}卦"
        tvHexagramName.text = hexagram.name
        tvSelectedLineName.text = "·$selectedLineName"

        // 右边：上卦卡片 + 下卦卡片（居中对齐）
        tvUpperTrigram.text = "${hexagram.upperTrigram.symbol}\n${hexagram.upperTrigram.name}（${hexagram.upperTrigram.nature}）"
        tvLowerTrigram.text = "${hexagram.lowerTrigram.symbol}\n${hexagram.lowerTrigram.name}（${hexagram.lowerTrigram.nature}）"

        // 底部：卦象含义（单独一行）
        tvOverallMeaning.text = hexagram.overallMeaning

        // 显示六爻
        displayLines(hexagram)

        // 显示选中的爻 (放到选中爻页面)
        tvSelectedLine.text = "【解卦】$selectedLineName：$selectedLineText\n\n$selectedLineDesc"

        // 显示多维度运势解读
        displayFortuneAnalysis(hexagram, selectedLineName)

        // 重置到运势详解页面
        switchTab(0)

        // 震动一次提示用户已解锁
        if (hasShared) {
            vibrator?.vibrate(100)
        }

        // 滚动到页面最下方，显示运势详情
        scrollView.post {
            scrollView.fullScroll(View.FOCUS_DOWN)
        }
    }

    // 显示运势分析（根据 hasShared 控制显示）
    private fun displayFortuneAnalysis(hexagram: Hexagram, lineName: String) {
        // 根据爻名获取索引
        val lineIndex = when(lineName) {
            "初爻" -> 0
            "二爻" -> 1
            "三爻" -> 2
            "四爻" -> 3
            "五爻" -> 4
            "上爻" -> 5
            else -> 0
        }
        
        // 获取运势数据
        val fortuneData = HexagramFortunes.getFortune(hexagram.number, lineIndex)
        
        // 如果已分享，显示完整内容；否则显示模糊提示
        if (hasShared) {
            // 显示运势内容
            tvCareerContent.text = fortuneData?.运势 ?: "暂无数据"
            tvWealthContent.text = fortuneData?.财运 ?: "暂无数据"
            tvHealthContent.text = fortuneData?.健康 ?: "暂无数据"
            tvFamilyContent.text = fortuneData?.家庭 ?: "暂无数据"
            
            // 设置标题
            findViewById<TextView>(R.id.tvCareerTitle).text = "📊 运势 ▼"
            findViewById<TextView>(R.id.tvWealthTitle).text = "💰 财运 ▼"
            findViewById<TextView>(R.id.tvHealthTitle).text = "🏃 健康 ▼"
            findViewById<TextView>(R.id.tvFamilyTitle).text = "🏠 家庭 ▼"
            
            // 显示所有卡片
            findViewById<View>(R.id.cardLove)?.visibility = View.GONE
            findViewById<View>(R.id.cardRelation)?.visibility = View.GONE
            findViewById<View>(R.id.cardStock)?.visibility = View.GONE
            findViewById<View>(R.id.cardCareer)?.visibility = View.VISIBLE
            findViewById<View>(R.id.cardWealth)?.visibility = View.VISIBLE
            findViewById<View>(R.id.cardHealth)?.visibility = View.VISIBLE
            findViewById<View>(R.id.cardFamily)?.visibility = View.VISIBLE
            
            // 显示内容
            tvCareerContent.visibility = View.VISIBLE
            tvWealthContent.visibility = View.VISIBLE
            tvHealthContent.visibility = View.VISIBLE
            tvFamilyContent.visibility = View.VISIBLE
        } else {
            // 显示模糊提示
            pageFortune.removeAllViews()
            val blurView = layoutInflater.inflate(R.layout.view_share_blur, pageFortune, false)
            blurView.findViewById<TextView>(R.id.shareBlurText)?.text = "🔒 运势详解已隐藏"
            blurView.findViewById<TextView>(R.id.shareBlurHint)?.text = "分享给好友即可查看运势详解\n或等待10秒后自动解锁"
            
            val shareBtn = blurView.findViewById<MaterialButton>(R.id.shareBtn)
            shareBtn?.text = "分享解锁"
            shareBtn?.setOnClickListener {
                showShareDialog()
            }
            
            // 开始10秒广告倒计时
            startAdCountdown(blurView)
            
            pageFortune.addView(blurView)
        }
    }

    // 开始广告倒计时（简化版，直接解锁）
    private fun startAdCountdown(blurView: View) {
        // 10秒后自动解锁
        adCountdownHandler?.postDelayed({
            handleShareUnlock()
        }, 10000)
    }

    // 显示六爻（根据 hasShared 控制显示）
    private fun displayLines(hexagram: Hexagram) {
        layoutLines.removeAllViews()

        val lineNames = arrayOf("初爻", "二爻", "三爻", "四爻", "五爻", "上爻")

        if (hasShared) {
            // 已分享，显示完整内容
            for (i in 0 until 6) {
                val lineName = lineNames[i]
                val lineText = hexagram.lines[i]
                val description = hexagram.lineDescriptions[i]

                val lineInfo = TextView(this)
                lineInfo.text = "$lineName：$lineText"
                lineInfo.textSize = 16f
                lineInfo.setTextColor(Color.BLACK)

                val descView = TextView(this)
                descView.text = description
                descView.textSize = 14f
                descView.setTextColor(Color.DKGRAY)
                descView.setPadding(0, 6, 0, 0)

                val container = LinearLayout(this)
                container.orientation = LinearLayout.VERTICAL
                container.setPadding(0, 12, 0, 12)
                container.addView(lineInfo)
                container.addView(descView)

                layoutLines.addView(container)
            }
        } else {
            // 未分享，显示模糊提示
            val blurView = layoutInflater.inflate(R.layout.view_share_blur, layoutLines, false)
            blurView.findViewById<TextView>(R.id.shareBlurText)?.text = "🔒 六爻详解已隐藏"
            blurView.findViewById<TextView>(R.id.shareBlurHint)?.text = "分享给好友即可查看六爻详解\n或等待10秒后自动解锁"
            
            val shareBtn = blurView.findViewById<MaterialButton>(R.id.shareBtn)
            shareBtn?.text = "分享解锁"
            shareBtn?.setOnClickListener {
                showShareDialog()
            }
            
            // 开始10秒广告倒计时
            startAdCountdown(blurView)
            
            layoutLines.addView(blurView)
        }
    }

    // 显示选中爻（根据 hasShared 控制显示）
    private fun displaySelectedLine() {
        if (!hasShared) {
            // 显示模糊提示
            pageSelected.removeAllViews()
            val blurView = layoutInflater.inflate(R.layout.view_share_blur, pageSelected, false)
            blurView.findViewById<TextView>(R.id.shareBlurText)?.text = "🔒 选中爻详解已隐藏"
            blurView.findViewById<TextView>(R.id.shareBlurHint)?.text = "分享给好友即可查看选中爻详解\n或等待10秒后自动解锁"
            
            val shareBtn = blurView.findViewById<MaterialButton>(R.id.shareBtn)
            shareBtn?.text = "分享解锁"
            shareBtn?.setOnClickListener {
                showShareDialog()
            }
            
            // 开始10秒广告倒计时
            startAdCountdown(blurView)
            
            pageSelected.addView(blurView)
        }
    }

    // 显示分享引导弹窗
    private fun showShareDialog() {
        AlertDialog.Builder(this)
            .setTitle("分享解锁")
            .setMessage("分享大仙周易给好友，即可立即解锁所有内容！")
            .setPositiveButton("立即分享") { _, _ ->
                shareApp()
            }
            .setNegativeButton("等待10秒") { dialog, _ ->
                dialog.dismiss()
            }
            .setCancelable(true)
            .show()
    }

    // 分享解锁（模拟）
    private fun handleShareUnlock() {
        // 2秒后自动解锁
        AlertDialog.Builder(this)
            .setTitle("正在解锁...")
            .setCancelable(false)
            .create()
            .show()

        Handler(Looper.getMainLooper()).postDelayed({
            // 解锁内容
            hasShared = true
            saveShareState()
            
            // 刷新UI
            refreshUI()
            
            AlertDialog.Builder(this)
                .setTitle("✅ 已解锁")
                .setMessage("内容已解锁，您可以查看完整的运势详解和六爻详解")
                .setPositiveButton("确定", null)
                .show()
        }, 2000)
    }

    // 保存分享状态
    private fun saveShareState() {
        val prefs = getSharedPreferences("pref", Context.MODE_PRIVATE)
        prefs.edit().putBoolean("hasShared", hasShared).apply()
    }

    // 读取分享状态
    private fun getSharedState(): Boolean {
        val prefs = getSharedPreferences("pref", Context.MODE_PRIVATE)
        return prefs.getBoolean("hasShared", false)
    }

    // 刷新UI（当分享状态改变时）
    private fun refreshUI() {
        // 停止广告倒计时
        adCountdownHandler?.removeCallbacksAndMessages(null)
        
        // 重新显示当前标签页的内容
        when (currentTab) {
            0 -> {
                // 运势详解
                pageFortune.removeAllViews()
                currentHexagram?.let {
                    val lineNames = arrayOf("初爻", "二爻", "三爻", "四爻", "五爻", "上爻")
                    displayFortuneAnalysis(it, lineNames[currentLineIndex])
                }
            }
            1 -> {
                // 选中爻
                pageSelected.removeAllViews()
                if (hasShared) {
                    // 显示内容
                    val textView = TextView(this)
                    textView.text = tvSelectedLine.text.toString()
                    textView.textSize = 16f
                    textView.setPadding(24, 16, 24, 16)
                    pageSelected.addView(textView)
                } else {
                    // 显示模糊提示
                    displaySelectedLine()
                }
            }
            2 -> {
                // 其他爻
                pageLines.removeAllViews()
                if (hasShared) {
                    // 显示内容
                    currentHexagram?.let {
                        displayLines(it)
                    }
                } else {
                    // 显示模糊提示
                    displayLines(currentHexagram!!)
                }
            }
        }
    }

    // 选项页切换
    private fun switchTab(tab: Int) {
        currentTab = tab
        // 重置所有tab样式
        tabLines.setBackgroundColor(Color.parseColor("#F5F5DC"))
        tabLines.setTextColor(Color.parseColor("#666666"))
        tabSelected.setBackgroundColor(Color.parseColor("#F5F5DC"))
        tabSelected.setTextColor(Color.parseColor("#666666"))
        tabFortune.setBackgroundColor(Color.parseColor("#F5F5DC"))
        tabFortune.setTextColor(Color.parseColor("#666666"))
        
        // 隐藏所有页面
        pageLines.visibility = View.GONE
        pageSelected.visibility = View.GONE
        pageFortune.visibility = View.GONE
        
        when(tab) {
            0 -> {
                // 运势详解
                tabFortune.setBackgroundColor(Color.parseColor("#FFECB3"))
                tabFortune.setTextColor(Color.parseColor("#8B4513"))
                pageFortune.visibility = View.VISIBLE
                // 重新加载运势分析
                currentHexagram?.let {
                    val lineNames = arrayOf("初爻", "二爻", "三爻", "四爻", "五爻", "上爻")
                    displayFortuneAnalysis(it, lineNames[currentLineIndex])
                }
            }
            1 -> {
                // 选中爻
                tabSelected.setBackgroundColor(Color.parseColor("#FFECB3"))
                tabSelected.setTextColor(Color.parseColor("#8B4513"))
                pageSelected.visibility = View.VISIBLE
                // 根据分享状态显示
                if (!hasShared) {
                    displaySelectedLine()
                }
            }
            2 -> {
                // 其他爻
                tabLines.setBackgroundColor(Color.parseColor("#FFECB3"))
                tabLines.setTextColor(Color.parseColor("#8B4513"))
                pageLines.visibility = View.VISIBLE
                // 根据分享状态显示
                if (!hasShared) {
                    pageLines.removeAllViews()
                    currentHexagram?.let {
                        displayLines(it)
                    }
                }
            }
        }
        
        // 切换标签时自动滚动到底部
        scrollView.post {
            scrollView.fullScroll(View.FOCUS_DOWN)
        }
    }

    private fun setupFoldableCard(cardId: Int, titleId: Int, contentId: Int) {
        val card = findViewById<LinearLayout>(cardId)
        val title = findViewById<TextView>(titleId)
        val content = findViewById<TextView>(contentId)
        
        card.setOnClickListener {
            if (content.visibility == View.VISIBLE) {
                content.visibility = View.GONE
                title.text = title.text.toString().replace("▼", "▶")
            } else {
                content.visibility = View.VISIBLE
                title.text = title.text.toString().replace("▶", "▼")
            }
        }
    }

    private fun showResultCard() {
        if (cardResult.visibility == View.GONE) {
            cardResult.visibility = View.VISIBLE
            cardResult.alpha = 0f
            cardResult.animate().alpha(1f).setDuration(300).start()
        }
    }

    override fun onCreateOptionsMenu(menu: android.view.Menu?): Boolean {
        menuInflater.inflate(R.menu.main, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            R.id.action_share -> {
                shareApp()
                return true
            }
            R.id.action_reset -> {
                resetShareState()
                return true
            }
            else -> return super.onOptionsItemSelected(item)
        }
    }

    // 分享应用
    private fun shareApp() {
        // 分享后自动解锁
        hasShared = true
        saveShareState()
        refreshUI()
        
        val shareIntent = Intent().apply {
            action = Intent.ACTION_SEND
            type = "text/plain"
            putExtra(Intent.EXTRA_TEXT, "我刚用大仙周易抽中了卦象，来看看你的运势如何！下载地址：https://github.com/daxian10086/1")
        }
        startActivity(Intent.createChooser(shareIntent, "分享大仙周易"))
    }

    // 重置分享状态
    private fun resetShareState() {
        hasShared = false
        saveShareState()
        refreshUI()
        AlertDialog.Builder(this)
            .setTitle("已重置")
            .setMessage("下次算卦时需要重新分享或等待10秒才能查看完整内容")
            .setPositiveButton("确定", null)
            .show()
    }

    private fun loadShareState() {
        hasShared = getSharedState()
    }
}
