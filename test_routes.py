"""
验证招聘管理模块路由注册
"""

from main import app

def test_routes():
    """测试所有招聘管理路由是否正确注册"""

    expected_routes = [
        # 招聘审批
        "/api/recruitment-approval/list",
        "/api/recruitment-approval/{approval_id}",

        # 岗位管理
        "/api/recruitment-position/list",
        "/api/recruitment-position/{position_id}",
        "/api/recruitment-position/{position_id}/publish",

        # 简历管理
        "/api/recruitment-resume/list",
        "/api/recruitment-resume/{resume_id}",
        "/api/recruitment-resume/{resume_id}/schedule-interview",
        "/api/recruitment-resume/{resume_id}/reject",

        # 渠道管理
        "/api/recruitment-channel/list",
        "/api/recruitment-channel/{channel_id}",

        # 面试管理
        "/api/recruitment-interview/list",
        "/api/recruitment-interview/{interview_id}",
        "/api/recruitment-interview/{interview_id}/feedback",

        # Offer管理
        "/api/recruitment-offer/list",
        "/api/recruitment-offer/{offer_id}",
        "/api/recruitment-offer/{offer_id}/approve",
        "/api/recruitment-offer/{offer_id}/send",

        # 仪表板
        "/api/recruitment-dashboard/stats",

        # 题库
        "/api/recruitment-question-bank/list",
        "/api/recruitment-question-bank/{question_id}",

        # 岗位画像
        "/api/recruitment-job-profile/list",
        "/api/recruitment-job-profile/{profile_id}",
    ]

    # 获取所有注册的路由
    registered_routes = [route.path for route in app.routes]

    print("=" * 60)
    print("招聘管理模块路由验证")
    print("=" * 60)

    missing_routes = []
    found_routes = []

    for route in expected_routes:
        if route in registered_routes:
            found_routes.append(route)
            print(f"[OK] {route}")
        else:
            missing_routes.append(route)
            print(f"[MISS] {route}")

    print("\n" + "=" * 60)
    print(f"总计: {len(expected_routes)} 个路由")
    print(f"已注册: {len(found_routes)} 个")
    print(f"缺失: {len(missing_routes)} 个")
    print("=" * 60)

    if missing_routes:
        print("\n缺失的路由:")
        for route in missing_routes:
            print(f"  - {route}")
        return False
    else:
        print("\n[OK] All routes registered successfully!")
        return True

if __name__ == "__main__":
    success = test_routes()
    exit(0 if success else 1)
