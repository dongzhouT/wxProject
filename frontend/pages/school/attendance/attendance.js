Page({
  data: {
    selectedDate: new Date().toISOString().split('T')[0],
    courses: [],
    selectedCourseIndex: 0,
    selectedCourse: null,
    attendanceList: []
  },

  onLoad: function() {
    this.loadCourses();
  },

  // 加载课程列表
  loadCourses: function() {
    const app = getApp();
    app.request('/school/courses', 'GET', {}, res => {
      if (res.code === 200) {
        this.setData({
          courses: res.data || [],
          selectedCourse: res.data && res.data.length > 0 ? res.data[0] : null
        });
      }
    });
  },

  // 绑定日期选择
  bindDateChange: function(e) {
    this.setData({
      selectedDate: e.detail.value
    });
  },

  // 绑定课程选择
  bindCourseChange: function(e) {
    const index = e.detail.value;
    this.setData({
      selectedCourseIndex: index,
      selectedCourse: this.data.courses[index]
    });
  },

  // 加载出勤记录
  loadAttendance: function() {
    if (!this.data.selectedCourse) {
      wx.showToast({
        title: '请选择课程',
        icon: 'none'
      });
      return;
    }

    const app = getApp();
    app.request('/school/attendance', 'GET', {
      courseId: this.data.selectedCourse.id,
      date: this.data.selectedDate
    }, res => {
      if (res.code === 200) {
        this.setData({
          attendanceList: res.data || []
        });
      }
    });
  },

  // 绑定状态变更
  bindStatusChange: function(e) {
    const index = e.currentTarget.dataset.id;
    const statusIndex = e.detail.value;
    const statuses = ['出勤', '缺勤', '迟到'];
    const newStatus = statuses[statusIndex];

    const attendanceList = [...this.data.attendanceList];
    const item = attendanceList.find(item => item.id === index);
    if (item) {
      item.status = newStatus;
      this.setData({
        attendanceList: attendanceList
      });
    }
  },

  // 保存出勤记录
  saveAttendance: function() {
    const app = getApp();
    app.request('/school/attendance', 'POST', {
      courseId: this.data.selectedCourse.id,
      date: this.data.selectedDate,
      attendanceList: this.data.attendanceList
    }, res => {
      if (res.code === 200) {
        wx.showToast({
          title: '保存成功',
          icon: 'none'
        });
      }
    });
  }
});