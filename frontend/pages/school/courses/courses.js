Page({
  data: {
    courses: [],
    searchText: ''
  },

  onLoad: function() {
    this.loadCourses();
  },

  onShow: function() {
    this.loadCourses();
  },

  // 加载课程数据
  loadCourses: function() {
    const app = getApp();
    app.request('/school/courses', 'GET', {}, res => {
      if (res.code === 200) {
        this.setData({
          courses: res.data || []
        });
      }
    });
  },

  // 输入搜索文本
  inputSearch: function(e) {
    this.setData({
      searchText: e.detail.value
    });
  },

  // 搜索课程
  search: function() {
    const app = getApp();
    app.request('/school/courses', 'GET', { search: this.data.searchText }, res => {
      if (res.code === 200) {
        this.setData({
          courses: res.data || []
        });
      }
    });
  },

  // 添加课程
  addCourse: function() {
    wx.navigateTo({
      url: '/pages/school/courses/edit'
    });
  },

  // 查看课程详情
  viewDetails: function(e) {
    const courseId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: '/pages/school/courses/details?courseId=' + courseId
    });
  },

  // 编辑课程
  editCourse: function(e) {
    const courseId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: '/pages/school/courses/edit?courseId=' + courseId
    });
  },

  // 删除课程
  deleteCourse: function(e) {
    const courseId = e.currentTarget.dataset.id;
    wx.showModal({
      title: '确认删除',
      content: '确定要删除这门课程吗？',
      success: res => {
        if (res.confirm) {
          const app = getApp();
          app.request('/school/courses/' + courseId, 'DELETE', {}, res => {
            if (res.code === 200) {
              wx.showToast({
                title: '删除成功',
                icon: 'none'
              });
              this.loadCourses();
            }
          });
        }
      }
    });
  }
});