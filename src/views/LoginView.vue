<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { DataAnalysis } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const account = ref('demo')
const password = ref('demo1234')
const auth = useAuthStore()
const router = useRouter()

function submit() {
  if (auth.login(account.value, password.value)) router.push('/dashboard')
  else ElMessage.error('演示登录：账号 demo，密码至少 6 位')
}
function enterDemo() {
  auth.demoLogin()
  router.push('/dashboard')
}
</script>

<template>
  <div class="auth-page">
    <section class="auth-panel">
      <div class="auth-brand"><div class="brand-mark"><DataAnalysis /></div><strong>StockLab</strong></div>
      <div class="auth-copy"><h1>欢迎回到你的研究终端</h1><p>登录后继续跟踪市场、策略和交易计划。</p></div>
      <form class="auth-form" @submit.prevent="submit">
        <div class="form-field"><label>用户名 / 邮箱</label><input v-model="account" autocomplete="username" placeholder="demo" /></div>
        <div class="form-field"><label>密码</label><input v-model="password" autocomplete="current-password" type="password" placeholder="至少 6 位" /></div>
        <button class="btn primary auth-submit" type="submit">登录</button>
        <button class="btn soft auth-demo" type="button" @click="enterDemo">进入演示账户</button>
      </form>
      <div class="auth-switch">还没有账户？<RouterLink to="/register">创建账户</RouterLink></div>
      <div class="auth-hint"><b>Demo Account</b><br />用户名 demo · 密码 demo1234<br />本原型不连接真实账户或实时行情。</div>
    </section>
    <section class="auth-visual">
      <span class="visual-kicker">Personal research terminal</span>
      <h2>让每一个判断，<br />都有数据可以回看。</h2>
      <p>从市场扫描到交易复盘，StockLab 把股票研究过程组织成一套清晰、可解释、可持续验证的个人工作流。</p>
      <div class="auth-features"><div class="auth-feature"><strong>3 Scores</strong><span>技术 · 股性 · 位置</span></div><div class="auth-feature"><strong>9 Engines</strong><span>从行情到回测</span></div><div class="auth-feature"><strong>1 Workflow</strong><span>发现 · 跟踪 · 复盘</span></div></div>
    </section>
  </div>
</template>
