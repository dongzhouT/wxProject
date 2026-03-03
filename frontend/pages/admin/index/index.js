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

  // 导航到学校管理页面
  navigateToSchools: function() {
    wx.navigateTo({
      url: '/pages/admin/schools/schools'
    });
  },

  // 导航到系统配置页面
  navigateToSystem: function() {
    wx.showToast({
      title: '系统配置功能开发中',
      icon: 'none'
    });
  },

  // 导航到数据统计页面
  navigateToStats: function() {
    wx.showToast({
      title: '数据统计功能开发中',
      icon: 'none'
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
