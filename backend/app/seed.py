from datetime import datetime, timedelta

from database import SessionLocal
from model.user import User
from model.lab import Lab
from model.equipment import Equipment
from model.reservation import Reservation
from utils.password import hash_password


def seed_if_empty():
    """空库时自动写入演示数据。

    用途：云端部署（如 Render 免费档）使用临时磁盘，服务重启后数据库被清空，
    重启时调用本函数即可恢复到"开箱可演示"的状态；本地已有数据则完全不受影响。

    演示账号：
        admin   / admin123  管理员（可审核预约、管理用户/实验室/设备）
        student / 123456    学生（可预约实验室、与 AI 对话）
    """
    db = SessionLocal()
    try:
        # 只要用户表有数据就认为已初始化过，直接跳过（幂等）
        if db.query(User).count() > 0:
            return

        # ---------- 用户 ----------
        # role: student-学生 admin-管理员，status: 1-启用
        admin = User(username='admin', password=hash_password('admin123'),
                     name='系统管理员', role='admin', status=1)
        student = User(username='student', password=hash_password('123456'),
                       name='张同学', role='student',
                       email='student@demo.com', phone='13800000000', status=1)
        db.add_all([admin, student])
        db.flush()  # 先写入拿到自增 id（如 admin.id=1、student.id=2），供下面外键使用

        # ---------- 实验室 ----------
        # open_time/close_time 为字符串时间段，status: 1-开放
        lab1 = Lab(name='人工智能实验室', capacity=40, status=1,
                   description='配备 GPU 工作站，支持深度学习模型训练与推理实验',
                   location='实验楼 A301', open_time='08:00', close_time='22:00')
        lab2 = Lab(name='网络安全实验室', capacity=24, status=1,
                   description='配备攻防靶场与流量分析平台，可开展渗透测试演练',
                   location='实验楼 B205', open_time='08:30', close_time='21:30')
        lab3 = Lab(name='嵌入式开发实验室', capacity=30, status=1,
                   description='配备示波器、开发板与焊接工作台，支持单片机与 IoT 开发',
                   location='实验楼 C102', open_time='09:00', close_time='21:00')
        db.add_all([lab1, lab2, lab3])
        db.flush()  # 拿到实验室 id（lab1.id=1、lab2.id=2、lab3.id=3）

        # ---------- 设备 ----------
        # status: 1-正常 0-维修，quantity 为可用数量
        stm32 = Equipment(lab_id=lab3.id, name='STM32 开发板', spec='STM32F407',
                          description='单片机与嵌入式开发', quantity=15, status=1)
        db.add_all([
            Equipment(lab_id=lab1.id, name='GPU 工作站', spec='RTX 4090 / 128G 内存',
                      description='深度学习训练服务器', quantity=10, status=1),
            Equipment(lab_id=lab1.id, name='边缘计算开发板', spec='Jetson Orin Nano',
                      description='模型部署与边缘推理实验', quantity=8, status=1),
            Equipment(lab_id=lab2.id, name='网络攻防靶机', spec='Kali Linux',
                      description='渗透测试演练平台', quantity=12, status=1),
            Equipment(lab_id=lab2.id, name='协议分析仪', spec='Wireshark专用平台',
                      description='抓包与流量分析', quantity=6, status=1),
            Equipment(lab_id=lab3.id, name='数字示波器', spec='200MHz 带宽',
                      description='信号测量与调试', quantity=10, status=1),
            stm32,
        ])
        db.flush()  # 拿到设备自增 id，供预约外键使用

        # ---------- 预约 ----------
        # status: 0-待审批 1-已通过 2-已拒绝 3-取消；date/start_time/end_time 均为字符串
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        day_after = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
        db.add_all([
            # 待审批：管理员登录后可以在"预约审核"页看到并审批这条
            Reservation(user_id=student.id, lab_id=lab1.id, equipment_id=None,
                        date=tomorrow, start_time='09:00', end_time='12:00',
                        remark='深度学习课程实验', status=0),
            # 已通过：带设备的预约，演示"预约实验室+设备"两种类型
            Reservation(user_id=student.id, lab_id=lab3.id, equipment_id=stm32.id,
                        date=day_after, start_time='14:00', end_time='17:00',
                        remark='嵌入式课程设计调试', status=1),
        ])

        db.commit()
    finally:
        db.close()
