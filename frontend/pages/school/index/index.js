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

  // 导航到家长管理页面
  navigateToParents: function() {
    wx.navigateTo({
      url: '/pages/school/parents/parents'
    });
  },

  // 导航到课程管理页面
  navigateToCourses: function() {
    wx.navigateTo({
      url: '/pages/school/courses/courses'
    });
  },

  // 导航到出勤管理页面
  navigateToAttendance: function() {
    wx.navigateTo({
      url: '/pages/school/attendance/attendance'
    });
  },

  // 导航到消课操作页面
  navigateTo消课: function() {
    wx.navigateTo({
      url: '/pages/school/consume/consume'
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
