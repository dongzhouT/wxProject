Page({
  data: {
    courseId: null,
    course: {
      name: '',
      category: '',
      price: '',
      description: ''
    }
  },

  onLoad: function(options) {
    if (options.courseId) {
      this.setData({
        courseId: options.courseId
      });
      this.loadCourseDetail();
    }
  },

  // 加载课程详情
  loadCourseDetail: function() {
    const app = getApp();
    app.request('/school/courses/' + this.data.courseId, 'GET', {}, res => {
      if (res.code === 200) {
        this.setData({
          course: res.data || {
            name: '',
            category: '',
            price: '',
            description: ''
          }
        });
      }
    });
  },

  // 编辑课程
  editCourse: function() {
    wx.navigateTo({
      url: '/pages/school/courses/edit?courseId=' + this.data.courseId
    });
  },

  // 删除课程
  deleteCourse: function() {
    wx.showModal({
      title: '确认删除',
      content: '确定要删除这门课程吗？',
      success: res => {
        if (res.confirm) {
          const app = getApp();
          app.request('/school/courses/' + this.data.courseId, 'DELETE', {}, res => {
            if (res.code === 200) {
              wx.showToast({
                title: '删除成功',
                icon: 'none'
              });
              wx.navigateBack();
            }
          });
        }
      }
    });
  }
});