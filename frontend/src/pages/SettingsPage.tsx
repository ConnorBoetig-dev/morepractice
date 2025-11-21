import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { useAuthStore } from '@/stores/authStore'
import { apiClient } from '@/services/api'
import { User, Lock, LogOut, Trash2, AlertTriangle } from 'lucide-react'

export function SettingsPage() {
  const navigate = useNavigate()
  const { user, logout, updateUser } = useAuthStore()
  const [username, setUsername] = useState(user?.username || '')
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const updateProfileMutation = useMutation({
    mutationFn: async (data: { username?: string }) => {
      const response = await apiClient.patch('/auth/profile', data)
      return response.data
    },
    onSuccess: (data) => {
      updateUser(data.user)
      setMessage({ type: 'success', text: 'Profile updated successfully!' })
    },
    onError: () => {
      setMessage({ type: 'error', text: 'Failed to update profile' })
    },
  })

  const changePasswordMutation = useMutation({
    mutationFn: async (data: { current_password: string; new_password: string }) => {
      const response = await apiClient.post('/auth/change-password', data)
      return response.data
    },
    onSuccess: () => {
      setMessage({ type: 'success', text: 'Password changed successfully!' })
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
    },
    onError: () => {
      setMessage({ type: 'error', text: 'Failed to change password. Check your current password.' })
    },
  })

  const handleUpdateProfile = () => {
    if (username !== user?.username) {
      updateProfileMutation.mutate({ username })
    }
  }

  const handleChangePassword = () => {
    if (newPassword !== confirmPassword) {
      setMessage({ type: 'error', text: 'Passwords do not match' })
      return
    }
    if (newPassword.length < 8) {
      setMessage({ type: 'error', text: 'Password must be at least 8 characters' })
      return
    }
    changePasswordMutation.mutate({ current_password: currentPassword, new_password: newPassword })
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="p-6 max-w-2xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-neutral-900 dark:text-slate-100 mb-2">Settings</h1>
        <p className="text-neutral-600 dark:text-slate-400">Manage your account settings</p>
      </div>

      {message && (
        <div
          className={`mb-6 p-4 rounded-lg ${
            message.type === 'success'
              ? 'bg-success-50 text-success-700 border border-success-200'
              : 'bg-error-50 text-error-700 border border-error-200'
          }`}
        >
          {message.text}
        </div>
      )}

      {/* Profile Settings */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center">
            <User className="h-5 w-5 mr-2" />
            Profile
          </CardTitle>
          <CardDescription>Update your profile information</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-slate-300 mb-1">Username</label>
            <Input value={username} onChange={(e) => setUsername(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-slate-300 mb-1">Email</label>
            <Input value={user?.email || ''} disabled className="bg-neutral-50 dark:bg-slate-600" />
            <p className="text-xs text-neutral-500 dark:text-slate-400 mt-1">Email cannot be changed</p>
          </div>
          <Button
            onClick={handleUpdateProfile}
            disabled={username === user?.username}
            isLoading={updateProfileMutation.isPending}
          >
            Save Changes
          </Button>
        </CardContent>
      </Card>

      {/* Password Settings */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center">
            <Lock className="h-5 w-5 mr-2" />
            Change Password
          </CardTitle>
          <CardDescription>Update your password</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-slate-300 mb-1">Current Password</label>
            <Input
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-slate-300 mb-1">New Password</label>
            <Input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-slate-300 mb-1">Confirm New Password</label>
            <Input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
            />
          </div>
          <Button
            onClick={handleChangePassword}
            disabled={!currentPassword || !newPassword || !confirmPassword}
            isLoading={changePasswordMutation.isPending}
          >
            Change Password
          </Button>
        </CardContent>
      </Card>

      {/* Danger Zone */}
      <Card className="border-error-200">
        <CardHeader>
          <CardTitle className="flex items-center text-error-600">
            <AlertTriangle className="h-5 w-5 mr-2" />
            Danger Zone
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-neutral-50 dark:bg-slate-600 rounded-lg">
            <div>
              <p className="font-medium text-neutral-900 dark:text-slate-100">Log out</p>
              <p className="text-sm text-neutral-600 dark:text-slate-400">Sign out of your account</p>
            </div>
            <Button variant="secondary" onClick={handleLogout}>
              <LogOut className="h-4 w-4 mr-2" />
              Log out
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
