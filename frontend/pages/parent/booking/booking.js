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
        // 获取用户已预约的课程列表
        let bookedCourses = wx.getStorageSync('bookedCourses') || [];
        // 确保类型一致
        bookedCourses = bookedCourses.map(id => parseInt(id));
        
        // 为每个课程添加booked状态
        const courseList = (res.data || []).map(course => {
          return {
            ...course,
            booked: bookedCourses.includes(parseInt(course.id))
          };
        });
        
        this.setData({
          courseList: courseList
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
        // 获取已预约课程列表
        let bookedCourses = wx.getStorageSync('bookedCourses') || [];
        // 确保类型一致
        bookedCourses = bookedCourses.map(id => parseInt(id));
        // 添加新预约的课程
        if (!bookedCourses.includes(parseInt(courseId))) {
          bookedCourses.push(parseInt(courseId));
          wx.setStorageSync('bookedCourses', bookedCourses);
        }
        
        wx.showToast({
          title: '预约成功',
          icon: 'none'
        });
        // 重新加载课程列表
        this.loadCourses();
      } else {
        wx.showToast({
          title: res.message || '预约失败',
          icon: 'none'
        });
      }
    });
  },

  // 取消预约
  cancelBooking: function(e) {
    const courseId = e.currentTarget.dataset.id;
    
    wx.showModal({
      title: '取消预约',
      content: '确定要取消预约吗？',
      success: (res) => {
        if (res.confirm) {
          const app = getApp();
          app.request('/parent/booking/cancel', 'POST', {
            course_id: courseId
          }, res => {
            if (res.code === 200) {
              // 获取已预约课程列表
              let bookedCourses = wx.getStorageSync('bookedCourses') || [];
              // 确保类型一致
              bookedCourses = bookedCourses.map(id => parseInt(id));
              // 移除取消预约的课程
              bookedCourses = bookedCourses.filter(id => id !== parseInt(courseId));
              wx.setStorageSync('bookedCourses', bookedCourses);
              
              wx.showToast({
                title: '取消预约成功',
                icon: 'none'
              });
              // 重新加载课程列表
              this.loadCourses();
            } else {
              wx.showToast({
                title: res.message || '取消预约失败',
                icon: 'none'
              });
            }
          });
        }
      }
    });
  }
});