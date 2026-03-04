Page({
  data: {
    notifications: []
  },

  onLoad: function() {
    // 加载通知数据
    this.loadNotifications();
  },

  // 加载通知数据
  loadNotifications: function() {
    const app = getApp();
    app.request('/parent/notifications', 'GET', {}, res => {
      if (res.code === 200) {
        this.setData({
          notifications: res.data || []
        });
      }
    });
  }
});