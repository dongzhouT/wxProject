Page({
  data: {
    courseId: null,
    weekDays: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    course: {
      name: '',
      price: '',
      description: '',
      schedule: [],
      time: '',
      teacher: '',
      max_students: 10
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
        const courseData = res.data || {};
        this.setData({
          course: {
            name: courseData.name || '',
            price: courseData.price || '',
            description: courseData.description || '',
            schedule: courseData.schedule || [],
            time: courseData.time || '',
            teacher: courseData.teacher || '',
            max_students: courseData.max_students || 10
          }
        });
      } else {
        wx.showToast({
          title: res.message || '课程不存在',
          icon: 'none'
        });
        wx.navigateBack();
      }
    });
  },

  // 输入课程名称
  inputName: function(e) {
    this.setData({
      'course.name': e.detail.value
    });
  },

  // 输入课程类别
  inputCategory: function(e) {
    this.setData({
      'course.category': e.detail.value
    });
  },

  // 输入课程价格
  inputPrice: function(e) {
    this.setData({
      'course.price': e.detail.value
    });
  },

  // 输入课程描述
  inputDescription: function(e) {
    this.setData({
      'course.description': e.detail.value
    });
  },

  // 输入上课时间
  inputTime: function(e) {
    this.setData({
      'course.time': e.detail.value
    });
  },

  // 输入教师
  inputTeacher: function(e) {
    this.setData({
      'course.teacher': e.detail.value
    });
  },

  // 输入最大人数
  inputMaxStudents: function(e) {
    this.setData({
      'course.max_students': parseInt(e.detail.value) || 10
    });
  },

  // 切换开课时间
  toggleSchedule: function(e) {
    const day = e.currentTarget.dataset.day;
    const schedule = [...this.data.course.schedule];
    
    if (e.detail.value.length > 0) {
      // 选中
      if (!schedule.includes(day)) {
        schedule.push(day);
      }
    } else {
      // 取消选中
      const index = schedule.indexOf(day);
      if (index > -1) {
        schedule.splice(index, 1);
      }
    }
    
    this.setData({
      'course.schedule': schedule
    });
  },

  // 保存课程信息
  saveCourse: function() {
    const { courseId, course } = this.data;
    
    if (!course.name) {
      wx.showToast({
        title: '请输入课程名称',
        icon: 'none'
      });
      return;
    }

    if (!course.price) {
      wx.showToast({
        title: '请输入课程价格',
        icon: 'none'
      });
      return;
    }

    const app = getApp();
    const url = courseId ? '/school/courses/' + courseId : '/school/courses';
    const method = courseId ? 'PUT' : 'POST';
    
    // 构建请求数据
    const requestData = {
      name: course.name,
      price: parseFloat(course.price),
      description: course.description,
      schedule: course.schedule,
      time: course.time,
      teacher: course.teacher,
      max_students: course.max_students
    };
    
    app.request(url, method, requestData, res => {
      if (res.code === 200) {
        wx.showToast({
          title: courseId ? '更新成功' : '添加成功',
          icon: 'none'
        });
        wx.navigateBack();
      }
    });
  }
});