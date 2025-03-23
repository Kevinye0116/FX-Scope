<template>
  <el-dialog
    v-model="dialogVisible"
    title="账号设置"
    width="500px"
    :show-close="true"
    destroy-on-close
    @update:modelValue="$emit('update:visible')"
  >
    <div class="account-dialog-content">
      <!-- 头像上传 -->
      <div class="account-info-item">
        <div class="avatar-container">
          <el-avatar
            :size="60"
            :style="{ backgroundColor: avatarBgColor }"
            v-if="!avatarUrl && avatarText"
          >
            {{ avatarText }}
          </el-avatar>
          <el-avatar :size="60" :src="avatarUrl" :icon="UserFilled" v-else />
        </div>
      </div>

      <!-- 用户名 -->
      <div class="account-info-item">
        <span class="label">用户名</span>
        <div class="value-wrapper">
          <template v-if="!editingUsername">
            <span class="value">{{ userInfo.username }}</span>
            <div class="spacer"></div>
            <el-button link type="primary" @click="startEditUsername">修改</el-button>
          </template>
          <template v-else>
            <el-input
              v-model="tempUsername"
              style="width: 200px"
              @keyup.enter="confirmUpdate('username')"
            />
            <div class="spacer"></div>
            <div class="button-group">
              <el-button link type="primary" @click="confirmUpdate('username')">确定</el-button>
              <el-button link @click="cancelEdit('username')">取消</el-button>
            </div>
          </template>
        </div>
      </div>

      <!-- 邮箱 -->
      <div class="account-info-item">
        <span class="label">邮箱</span>
        <div class="value-wrapper">
          <template v-if="!editingEmail">
            <span class="value">{{ userInfo.email }}</span>
            <div class="spacer"></div>
            <el-button link type="primary" @click="startEditEmail">修改</el-button>
          </template>
          <template v-else>
            <el-input
              v-model="tempEmail"
              style="width: 200px"
              @keyup.enter="confirmUpdate('email')"
            />
            <div class="spacer"></div>
            <div class="button-group">
              <el-button link type="primary" @click="confirmUpdate('email')">确定</el-button>
              <el-button link @click="cancelEdit('email')">取消</el-button>
            </div>
          </template>
        </div>
      </div>

      <!-- 删除账号 -->
      <div class="delete-account">
        <el-button type="danger" @click="handleDeleteAccount">删除账号</el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script>
import { UserFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { deleteAccount, updateUserInfo } from '../api/user'
import { useUserStore } from '../stores/user'

export default {
  name: 'SettingDialog',
  props: {
    visible: {
      type: Boolean,
      required: true,
    },
    userInfo: {
      type: Object,
      required: true,
    },
    avatarBgColor: {
      type: String,
      required: true,
    },
  },
  emits: ['update:visible', 'avatar-updated'],
  data() {
    return {
      UserFilled,
      avatarUrl: '',
      language: 'zh',
      editingUsername: false,
      editingEmail: false,
      tempUsername: '',
      tempEmail: '',
    }
  },
  computed: {
    dialogVisible: {
      get() {
        return this.visible
      },
      set(value) {
        this.$emit('update:visible', value)
      },
    },
    avatarText() {
      if (!this.userInfo.username) return ''
      const firstChar = this.userInfo.username.charAt(0)
      return firstChar
    },
  },
  setup() {
    const userStore = useUserStore()
    const router = useRouter()
    return { userStore, router }
  },
  methods: {
    handleAvatarSuccess(response) {
      this.avatarUrl = response.url
      this.$emit('avatar-updated', response.url)
    },
    handleDeleteAccount() {
      ElMessageBox.confirm('确定要删除账号吗？此操作不可恢复。', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      })
        .then(async () => {
          try {
            await deleteAccount()
            ElMessage.success('账号已删除')
            this.userStore.clearUserInfo()
            this.router.push('/auth')
          } catch (error) {
            ElMessage.error(error.response?.data?.message || '删除账号失败')
          }
        })
        .catch(() => {})
    },
    startEditUsername() {
      this.tempUsername = this.userInfo.username
      this.editingUsername = true
    },
    startEditEmail() {
      this.tempEmail = this.userInfo.email
      this.editingEmail = true
    },
    cancelEdit(field) {
      if (field === 'username') {
        this.editingUsername = false
      } else {
        this.editingEmail = false
      }
    },
    async confirmUpdate(field) {
      try {
        const data = {}
        if (field === 'username') {
          data.username = this.tempUsername
        } else {
          data.email = this.tempEmail
        }

        const response = await updateUserInfo(data)
        this.$emit('update:userInfo', {
          ...this.userInfo,
          ...response,
        })

        ElMessage.success('更新成功')
        this.editingUsername = false
        this.editingEmail = false
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '更新失败')
      }
    },
  },
}
</script>

<style scoped>
.account-dialog-content {
  padding: 20px 0;
}

.account-info-item {
  display: flex;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #eee;
}

.account-info-item:last-child {
  border-bottom: none;
}

.account-info-item .label {
  width: 80px;
  color: #606266;
  font-size: 15px;
}

.value-wrapper {
  display: flex;
  align-items: center;
  width: 100%;
  gap: 12px;
  min-height: 32px;
}

.spacer {
  flex-grow: 1;
}

.value {
  color: #333;
  font-size: 16px;
}

.avatar-container {
  display: flex;
  justify-content: center;
  width: 100%;
  padding: 10px 0;
}

.language-select {
  width: 140px;
}

.delete-account {
  margin-top: 10px;
  padding-top: 20px;
  text-align: left;
}

.button-group {
  display: flex;
  gap: 8px;
}

.el-avatar {
  font-size: 30px;
  font-weight: bold;
  text-transform: uppercase;
}
</style>
