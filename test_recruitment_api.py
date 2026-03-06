import requests
import json

BASE_URL = "http://localhost:8000"

# 测试数据
test_data = {
    "applicantId": 1,
    "applicantName": "张三",
    "departmentId": 111,
    "departmentName": "研发中心",
    "positionName": "高级前端工程师",
    "positionCode": "FE-001",
    "recruitCount": 2,
    "positionType": "full-time",
    "workLocation": "北京",
    "positionLevel": "P5",
    "expectedOnboardDate": "2026-04-01",
    "recruitReason": "new"
}

headers = {
    "Content-Type": "application/json",
    "x-user-id": "1",
    "x-user-role": "admin"
}

print("测试 POST /api/recruitment-approval (创建草稿)")
response = requests.post(f"{BASE_URL}/api/recruitment-approval", json=test_data, headers=headers)
print(f"状态码: {response.status_code}")
print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
