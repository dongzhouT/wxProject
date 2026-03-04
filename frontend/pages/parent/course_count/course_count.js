Page({
  data: {
    courseList: []
  },

  onLoad: function() {
    // 加载剩余课程数据
    this.loadCourseCount();
  },

  // 加载剩余课程数据
  loadCourseCount: function() {
    const app = getApp();
    app.request('/parent/course-count', 'GET', {}, res => {
      if (res.code === 200) {
        this.setData({
          courseList: res.data || []
        });
      }
    });
  }
});