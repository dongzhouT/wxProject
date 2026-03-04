Page({
  data: {
    courseList: []
  },

  onLoad: function() {
    // 加载可预约课程列表
    this.loadCourses();
  },

  // 加载可预约课程列表
  loadCourses: function() {
    const app = getApp();
    app.request('/parent/booking', 'GET', {}, res => {
      if (res.code === 200) {
        this.setData({
          courseList: res.data || []
        });
      }
    });
  },

  // 预约课程
  bookCourse: function(e) {
    const courseId = e.currentTarget.dataset.id;
    
    const app = getApp();
    app.request('/parent/booking', 'POST', {
      course_id: courseId
    }, res => {
      if (res.code === 200) {
        wx.showToast({
          title: '预约成功',
          icon: 'none'
        });
        // 重新加载课程列表
        this.loadCourses();
      }
    });
  }
});