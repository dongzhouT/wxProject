Page({
  data: {
    parentId: null,
    orderId: null,
    isEdit: false,
    types: ['课时包', '单次课程', '其他'],
    statuses: ['待支付', '已支付', '已取消'],
    order: {
      typeIndex: 0,
      statusIndex: 1,
      amount: '',
      total_lessons: '',
      course_name: ''
    }
  },

  onLoad: function(options) {
    if (options.parentId) {
      this.setData({
        parentId: options.parentId
      });
    }
    
    if (options.orderId) {
      this.setData({
        orderId: options.orderId,
        isEdit: true
      });
      this.loadOrderDetail();
    }
  },

  // 加载订单详情
  loadOrderDetail: function() {
    const app = getApp();
    app.request('/school/orders/' + this.data.orderId, 'GET', {}, res => {
      if (res.code === 200) {
        const order = res.data;
        this.setData({
          order: {
            typeIndex: this.data.types.indexOf(order.type || '课时包'),
            statusIndex: this.data.statuses.indexOf(order.status || '已支付'),
            amount: order.amount || '',
            total_lessons: order.lesson_packages && order.lesson_packages[0] ? order.lesson_packages[0].total_lessons : '',
            course_name: order.lesson_packages && order.lesson_packages[0] ? order.lesson_packages[0].course_name : ''
          }
        });
      }
    });
  },

  // 绑定类型选择
  bindTypeChange: function(e) {
    this.setData({
      'order.typeIndex': e.detail.value
    });
  },

  // 绑定状态选择
  bindStatusChange: function(e) {
    this.setData({
      'order.statusIndex': e.detail.value
    });
  },

  // 绑定金额输入
  bindAmountInput: function(e) {
    this.setData({
      'order.amount': e.detail.value
    });
  },

  // 绑定总课时输入
  bindTotalLessonsInput: function(e) {
    this.setData({
      'order.total_lessons': e.detail.value
    });
  },

  // 绑定课程名称输入
  bindCourseNameInput: function(e) {
    this.setData({
      'order.course_name': e.detail.value
    });
  },

  // 保存订单
  saveOrder: function() {
    const { parentId, orderId, isEdit, order, types, statuses } = this.data;
    
    // 验证输入
    if (!order.amount) {
      wx.showToast({ title: '请输入订单金额', icon: 'none' });
      return;
    }
    
    if (!order.total_lessons) {
      wx.showToast({ title: '请输入总课时', icon: 'none' });
      return;
    }
    
    if (!order.course_name) {
      wx.showToast({ title: '请输入课程名称', icon: 'none' });
      return;
    }
    
    const orderData = {
      type: types[order.typeIndex],
      status: statuses[order.statusIndex],
      amount: parseInt(order.amount),
      lesson_packages: [{
        course_name: order.course_name,
        total_lessons: parseInt(order.total_lessons),
        remaining_lessons: parseInt(order.total_lessons)
      }]
    };
    
    const app = getApp();
    const url = isEdit ? `/school/orders/${orderId}` : `/school/parents/${parentId}/orders`;
    const method = isEdit ? 'PUT' : 'POST';
    
    app.request(url, method, orderData, res => {
      if (res.code === 200) {
        wx.showToast({ title: isEdit ? '订单更新成功' : '订单添加成功' });
        setTimeout(() => {
          wx.navigateBack();
        }, 1500);
      }
    });
  }
});