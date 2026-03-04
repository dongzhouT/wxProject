Page({
  data: {
    userInfo: {}
  },

  onLoad: function() {
    // 获取用户信息
    const app = getApp();
    this.setData({
      userInfo: app.globalData.userInfo || {}
    });
  },

  onShow: function() {
    // 页面显示时刷新数据
    this.onLoad();
  },

  // 导航到课表页面
  navigateToSchedule: function() {
    wx.navigateTo({
      url: '/pages/parent/schedule/schedule'
    });
  },

  // 导航到请假申请页面
  navigateToLeave: function() {
    wx.navigateTo({
      url: '/pages/parent/leave/leave'
    });
  },

  // 导航到约课页面
  navigateToBooking: function() {
    wx.navigateTo({
      url: '/pages/parent/booking/booking'
    });
  },

  // 导航到剩余课程页面
  navigateToCourseCount: function() {
    wx.navigateTo({
      url: '/pages/parent/course_count/course_count'
    });
  },

  // 导航到通知页面
  navigateToNotifications: function() {
    wx.navigateTo({
      url: '/pages/parent/notifications/notifications'
    });
  },

  // 退出登录
  logout: function() {
    const app = getApp();
    
    // 清除本地存储的token和用户信息
    wx.removeStorageSync('token');
    wx.removeStorageSync('userInfo');
    wx.removeStorageSync('role');
    
    // 重置全局数据
    app.globalData.token = '';
    app.globalData.userInfo = null;
    app.globalData.role = '';
    
    // 跳转到登录页面（使用switchTab因为登录页面在tabBar中）
    wx.switchTab({
      url: '/pages/common/login/login'
    });
  }
});
