<template>
  <div class="wrapper">
    <!-- 添加logo -->
    <div class="main-title">
      <img src="/logo1.png" alt="FX-Scope Logo" />
    </div>

    <div class="container" :class="{ 'right-panel-active': isSignUpMode }">
      <!-- 注册表单 -->
      <div class="sign-up-container">
        <form @submit.prevent="handleRegister">
          <h1 style="margin-bottom: 20px">创建账号</h1>
          <input
            v-model="registerForm.username"
            type="text"
            placeholder="用户名"
            :class="{ error: registerErrors.username }"
          />
          <input
            v-model="registerForm.email"
            type="email"
            placeholder="邮箱"
            :class="{ error: registerErrors.email }"
          />
          <div class="password-input-container">
            <input
              v-model="registerForm.password"
              :type="showRegisterPassword1 ? 'text' : 'password'"
              placeholder="密码"
              :class="{ error: registerErrors.password }"
            />
            <el-icon
              v-if="registerForm.password"
              class="password-toggle"
              @click="showRegisterPassword1 = !showRegisterPassword1"
            >
              <component :is="showRegisterPassword1 ? View : Hide" />
            </el-icon>
          </div>
          <div class="password-input-container">
            <input
              v-model="registerForm.password2"
              :type="showRegisterPassword2 ? 'text' : 'password'"
              placeholder="确认密码"
              :class="{ error: registerErrors.password2 }"
            />
            <el-icon
              class="password-toggle"
              v-if="registerForm.password2"
              @click="showRegisterPassword2 = !showRegisterPassword2"
            >
              <component :is="showRegisterPassword2 ? View : Hide" />
            </el-icon>
          </div>
          <button class="form_btn" :disabled="loading">
            {{ loading ? '注册中...' : '注册' }}
          </button>
        </form>
      </div>

      <!-- 登录表单 -->
      <div class="sign-in-container">
        <form @submit.prevent="handleLogin">
          <h1 style="margin-bottom: 20px">登录</h1>
          <input
            v-model="loginForm.username"
            type="text"
            placeholder="用户名"
            :class="{ error: loginErrors.username }"
          />
          <div class="password-input-container">
            <input
              v-model="loginForm.password"
              :type="showLoginPassword ? 'text' : 'password'"
              placeholder="密码"
              :class="{ error: loginErrors.password }"
            />
            <el-icon
              v-if="loginForm.password"
              class="password-toggle"
              @click="showLoginPassword = !showLoginPassword"
            >
              <component :is="showLoginPassword ? View : Hide" />
            </el-icon>
          </div>
          <button class="form_btn" :disabled="loading">
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>
      </div>

      <!-- 切换面板 -->
      <div class="overlay-container">
        <div class="overlay-left">
          <h1 style="margin-left: 20px">欢迎回来！</h1>
          <p>登录您的账号，开始精彩体验</p>
          <button
            id="signIn"
            class="overlay_btn"
            @click="
              ;(isSignUpMode = false),
                Object.keys(registerErrors).forEach((key) => (registerErrors[key] = false))
            "
          >
            登录
          </button>
        </div>
        <div class="overlay-right">
          <h1 style="margin-left: 20px">你好，朋友！</h1>
          <p>开始注册，加入我们的行列吧</p>
          <button
            id="signUp"
            class="overlay_btn"
            @click="
              ;(isSignUpMode = true),
                Object.keys(loginErrors).forEach((key) => (loginErrors[key] = false))
            "
          >
            注册
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ElMessage } from 'element-plus'
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { login, register } from '../api/user'
import { useUserStore } from '../stores/user'
// 添加 element-plus 的图标
import { Hide, View } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const isSignUpMode = ref(false)

const showLoginPassword = ref(false)
const showRegisterPassword1 = ref(false)
const showRegisterPassword2 = ref(false)

// 登录表单
const loginForm = reactive({
  username: '',
  password: '',
})

const loginErrors = reactive({
  username: false,
  password: false,
})

// 注册表单
const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  password2: '',
})

const registerErrors = reactive({
  username: false,
  email: false,
  password: false,
  password2: false,
})

// 登录处理
const handleLogin = async () => {
  // 重置错误状态
  Object.keys(loginErrors).forEach((key) => (loginErrors[key] = false))

  // 表单验证
  let hasError = false
  if (!loginForm.username) {
    loginErrors.username = true
    hasError = true
  }
  if (!loginForm.password) {
    loginErrors.password = true
    hasError = true
  }

  if (hasError) {
    ElMessage.error('请填写完整的登录信息')
    return
  }

  try {
    loading.value = true
    const res = await login(loginForm)
    userStore.setToken(res.token.access)
    ElMessage.success('登录成功')
    router.push('/home')
  } catch (error) {
    const message =
      error.response?.data?.message ||
      error.response?.data?.detail ||
      error.message ||
      '用户名或密码错误'

    ElMessage.error(message)
    loginErrors.username = true
    loginErrors.password = true
    loginForm.username = ''
    loginForm.password = ''
  } finally {
    loading.value = false
  }
}

// 注册处理
const handleRegister = async () => {
  // 重置错误状态
  Object.keys(registerErrors).forEach((key) => (registerErrors[key] = false))

  // 表单验证
  let hasError = false
  if (!registerForm.username) {
    registerErrors.username = true
    hasError = true
  }
  if (!registerForm.email) {
    registerErrors.email = true
    hasError = true
  }
  if (!registerForm.password) {
    registerErrors.password = true
    hasError = true
  }
  if (!registerForm.password2) {
    registerErrors.password2 = true
    hasError = true
  }
  if (registerForm.password !== registerForm.password2) {
    registerErrors.password = true
    registerErrors.password2 = true
    ElMessage.error('两次输入的密码不一致')
    registerForm.password = ''
    registerForm.password2 = ''
    return
  }

  if (hasError) {
    ElMessage.error('请填写完整的注册信息')
    return
  }

  try {
    loading.value = true
    await register(registerForm)
    ElMessage.success('注册成功，请登录')
    isSignUpMode.value = false
  } catch (error) {
    let message = error.response?.data?.message || error.message
    if (error.response?.data?.errors) {
      const errors = error.response.data.errors
      if (errors.username) {
        message = '用户名已存在'
        registerErrors.username = true
      } else if (errors.email) {
        message = '该邮箱已被注册'
        registerErrors.email = true
      } else {
        message = errors.password[0]
        registerErrors.password = true
        registerErrors.password2 = true
        registerForm.password = ''
        registerForm.password2 = ''
      }
    }
    ElMessage.error(message)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.wrapper {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #ebecf0;
  overflow: hidden;
}

.container {
  border-radius: 10px;
  box-shadow: -5px -5px 10px #fff, 5px 5px 10px #babebc;
  position: relative;
  width: 768px;
  min-height: 480px;
  overflow: hidden;
}

form {
  background: #ebecf0;
  display: flex;
  flex-direction: column;
  padding: 0 50px;
  height: 100%;
  justify-content: center;
  align-items: center;
}

input {
  background: #eee;
  padding: 16px;
  margin: 8px 0;
  width: 85%;
  border: 0;
  outline: none;
  border-radius: 20px;
  box-shadow: inset 7px 2px 10px #babebc, inset -5px -5px 12px #fff;
}

input.error {
  border: 1px solid #ff4b2b;
}

button {
  border-radius: 20px;
  border: none;
  outline: none;
  font-size: 12px;
  font-weight: bold;
  padding: 15px 45px;
  margin: 14px;
  letter-spacing: 1px;
  text-transform: uppercase;
  cursor: pointer;
  transition: transform 80ms ease-in;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.form_btn {
  box-shadow: -5px -5px 10px #fff, 5px 5px 8px #babebc;
}

.form_btn:active:not(:disabled) {
  box-shadow: inset 1px 1px 2px #babebc, inset -1px -1px 2px #fff;
}

.overlay_btn {
  background-color: #ff4b2b;
  color: #fff;
  box-shadow: -5px -5px 10px #ff6b3f, 5px 5px 8px #bf4b2b;
}

.sign-in-container {
  position: absolute;
  left: 0;
  width: 50%;
  height: 100%;
  transition: all 0.5s;
}

.sign-up-container {
  position: absolute;
  left: 0;
  width: 50%;
  height: 100%;
  opacity: 0;
  transition: all 0.5s;
}

.overlay-left,
.overlay-right {
  display: flex;
  flex-direction: column;
  padding: 0 50px;
  justify-content: center;
  align-items: center;
  position: absolute;
  right: 0;
  width: 50%;
  height: 100%;
  background-color: #ff4b2b;
  color: #fff;
  transition: all 0.5s;
}

.overlay-left {
  opacity: 0;
}

.container.right-panel-active .sign-in-container {
  transform: translateX(100%);
  opacity: 0;
}

.container.right-panel-active .sign-up-container {
  transform: translateX(100%);
  opacity: 1;
  z-index: 2;
}

.container.right-panel-active .overlay-right {
  transform: translateX(-100%);
  opacity: 0;
}

.container.right-panel-active .overlay-left {
  transform: translateX(-100%);
  opacity: 1;
  z-index: 2;
}

h1 {
  font-weight: bold;
  margin: 0;
  color: #000;
}

.overlay-left h1,
.overlay-right h1 {
  color: #fff;
}

p {
  font-size: 16px;
  font-weight: bold;
  letter-spacing: 0.5px;
  margin: 20px 0 30px;
}

span {
  font-size: 12px;
  color: #000;
  letter-spacing: 0.5px;
  margin-bottom: 10px;
}

.social-links div {
  width: 40px;
  height: 40px;
  display: inline-flex;
  justify-content: center;
  align-items: center;
  margin: 0 5px;
  border-radius: 50%;
  box-shadow: -5px -5px 10px #fff, 5px 5px 8px #babebc;
  cursor: pointer;
}

.social-links a {
  color: #000;
}

.social-links div:active {
  box-shadow: inset 1px 1px 2px #babebc, inset -1px -1px 2px #fff;
}

.password-input-container {
  position: relative;
  width: 85%;
}

.password-input-container input {
  width: 100%;
  padding-right: 40px; /* 为图标留出空间 */
}

.password-toggle {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: #666;
}

.password-toggle:hover {
  color: #333;
}

.main-title {
  position: absolute;
  top: 15px;
  left: 51%;
  transform: translateX(-50%);
  z-index: 10;
  text-align: center;
}

.main-title img {
  height: 3.5em;
}
</style>
