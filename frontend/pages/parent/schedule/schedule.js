Page({
  data: {
    currentDate: '',
    scheduleList: []
  },

  onLoad: function() {
    // 设置当前日期
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const currentDate = `${year}-${month}-${day}`;
    
    this.setData({
      currentDate: currentDate
    });
    
    // 加载课程表数据
    this.loadSchedule();
  },

  // 绑定日期变化
  bindDateChange: function(e) {
    this.setData({
      currentDate: e.detail.value
    });
    // 重新加载课程表数据
    this.loadSchedule();
  },

  // 加载课程表数据
  loadSchedule: function() {
    const app = getApp();
    app.request('/parent/schedule', 'GET', { date: this.data.currentDate }, res => {
      if (res.code === 200) {
        this.setData({
          scheduleList: res.data || []
        });
      }
    });
  }
});