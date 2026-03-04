Page({
  data: {
    leaveDate: '',
    courseList: [],
    courseIndex: 0,
    leaveReason: ''
  },

  onLoad: function() {
    // 设置当前日期
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const leaveDate = `${year}-${month}-${day}`;
    
    this.setData({
      leaveDate: leaveDate
    });
    
    // 加载课程列表
    this.loadCourses();
  },

  // 绑定日期变化
  bindDateChange: function(e) {
    this.setData({
      leaveDate: e.detail.value
    });
  },

  // 绑定课程变化
  bindCourseChange: function(e) {
    this.setData({
      courseIndex: e.detail.value
    });
  },

  // 输入请假原因
  inputLeaveReason: function(e) {
    this.setData({
      leaveReason: e.detail.value
    });
  },

  // 加载课程列表
  loadCourses: function() {
    const app = getApp();
    app.request('/parent/courses', 'GET', {}, res => {
      if (res.code === 200) {
        const courseList = res.data.map(course => course.name);
        this.setData({
          courseList: courseList
        });
      }
    });
  },

  // 提交请假申请
  submitLeave: function() {
    const { leaveDate, courseList, courseIndex, leaveReason } = this.data;
    
    if (!leaveReason) {
      wx.showToast({
        title: '请输入请假原因',
        icon: 'none'
      });
      return;
    }
    
    const app = getApp();
    app.request('/parent/leave', 'POST', {
      date: leaveDate,
      course: courseList[courseIndex],
      reason: leaveReason
    }, res => {
      if (res.code === 200) {
        wx.showToast({
          title: '请假申请提交成功',
          icon: 'none'
        });
        wx.navigateBack();
      }
    });
  }
});