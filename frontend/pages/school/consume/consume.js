Page({
  data: {
    students: [],
    selectedStudentIndex: 0,
    selectedStudent: null,
    courses: [],
    selectedCourseIndex: 0,
    selectedCourse: null,
    consumeCount: 1,
    remainingLessons: 0
  },

  onLoad: function() {
    this.loadStudents();
    this.loadCourses();
  },

  // 加载学生列表
  loadStudents: function() {
    const app = getApp();
    app.request('/school/students', 'GET', {}, res => {
      if (res.code === 200) {
        this.setData({
          students: res.data || [],
          selectedStudent: res.data && res.data.length > 0 ? res.data[0] : null
        });
        this.updateRemainingLessons();
      }
    });
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
        this.updateRemainingLessons();
      }
    });
  },

  // 绑定学生选择
  bindStudentChange: function(e) {
    const index = e.detail.value;
    this.setData({
      selectedStudentIndex: index,
      selectedStudent: this.data.students[index]
    });
    this.updateRemainingLessons();
  },

  // 绑定课程选择
  bindCourseChange: function(e) {
    const index = e.detail.value;
    this.setData({
      selectedCourseIndex: index,
      selectedCourse: this.data.courses[index]
    });
    this.updateRemainingLessons();
  },

  // 输入消课数量
  inputConsumeCount: function(e) {
    const count = parseInt(e.detail.value) || 1;
    this.setData({
      consumeCount: count
    });
  },

  // 更新剩余课时
  updateRemainingLessons: function() {
    if (this.data.selectedStudent && this.data.selectedCourse) {
      // 模拟剩余课时
      const remaining = 20; // 实际项目中应该从后端获取
      this.setData({
        remainingLessons: remaining
      });
    }
  },

  // 确认消课
  consumeLessons: function() {
    if (!this.data.selectedStudent || !this.data.selectedCourse) {
      wx.showToast({
        title: '请选择学生和课程',
        icon: 'none'
      });
      return;
    }

    if (this.data.consumeCount > this.data.remainingLessons) {
      wx.showToast({
        title: '消课数量超过剩余课时',
        icon: 'none'
      });
      return;
    }

    const app = getApp();
    app.request('/school/consume', 'POST', {
      studentId: this.data.selectedStudent.id,
      courseId: this.data.selectedCourse.id,
      count: this.data.consumeCount
    }, res => {
      if (res.code === 200) {
        wx.showToast({
          title: '消课成功',
          icon: 'none'
        });
        // 重置表单
        this.setData({
          consumeCount: 1
        });
        this.updateRemainingLessons();
      }
    });
  }
});