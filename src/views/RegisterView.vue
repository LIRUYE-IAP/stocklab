<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { DataAnalysis } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const form = reactive({ username: '', email: '', password: '', confirm: '' })
const router = useRouter()
const auth = useAuthStore()
function submit() {
  if (!form.username || !form.email || form.password.length < 6) return ElMessage.warning('请完整填写信息，密码至少 6 位')
  if (form.password !== form.confirm) return ElMessage.warning('两次输入的密码不一致')
  auth.demoLogin()
  ElMessage.success('演示账户已创建')
  router.push('/dashboard')
}
</script>

<template>
  <div class="auth-page">
    <section class="auth-panel">
      <div class="auth-brand"><div class="brand-mark"><DataAnalysis /></div><strong>StockLab</strong></div>
      <div class="auth-copy"><h1>创建你的研究空间</h1><p>自选、策略、预警和复盘都将归属于这个账户。</p></div>
      <form class="auth-form" @submit.prevent="submit">
        <div class="grid-2"><div class="form-field"><label>用户名</label><input v-model="form.username" placeholder="研究者名称" /></div><div class="form-field"><label>邮箱</label><input v-model="form.email" type="email" placeholder="name@example.com" /></div></div>
        <div class="form-field"><label>密码</label><input v-model="form.password" type="password" placeholder="至少 6 位" /></div>
        <div class="form-field"><label>确认密码</label><input v-model="form.confirm" type="password" placeholder="再次输入密码" /></div>
        <button class="btn primary auth-submit" type="submit">创建账户</button>
      </form>
      <div class="auth-switch">已有账户？<RouterLink to="/login">返回登录</RouterLink></div>
      <div class="auth-hint">当前为前端演示注册。生产版将使用 Argon2 密码哈希、JWT 和数据库级用户隔离。</div>
    </section>
    <section class="auth-visual">
      <span class="visual-kicker">Your data, your process</span>
      <h2>不是新的行情门户，<br />而是你的研究档案。</h2>
      <p>保存筛选逻辑、入场原因和退出复盘。时间久了，你会真正看见自己如何做出判断。</p>
      <div class="auth-features"><div class="auth-feature"><strong>Watch</strong><span>自选与动态变化</span></div><div class="auth-feature"><strong>Verify</strong><span>策略历史统计</span></div><div class="auth-feature"><strong>Review</strong><span>交易周期复盘</span></div></div>
    </section>
  </div>
</template>
