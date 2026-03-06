#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试菜单排序 API
Created: 2026-03-06
Task: #37 - 菜单接口排序字段处理
"""

import sys
import os
import requests
import json

# API 基础 URL
BASE_URL = "http://localhost:8000/api"


def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_get_menus():
    """测试获取菜单列表"""
    print_section("Test 1: Get All Menus")

    response = requests.get(f"{BASE_URL}/admin/menus")
    if response.status_code == 200:
        data = response.json()
        menus = data.get('data', [])
        print(f"[OK] Retrieved {len(menus)} top-level menus")

        # 显示前5个菜单的排序信息
        for menu in menus[:5]:
            print(f"  ID: {menu['id']:3d} | Name: {menu['menu_name']:30s} | Sort: {menu['sort_order']:3d}")
    else:
        print(f"[ERROR] Failed to get menus: {response.status_code}")
        print(response.text)


def test_create_menu():
    """测试创建菜单（自动设置 sort_order）"""
    print_section("Test 2: Create Menu with Auto Sort Order")

    menu_data = {
        "menu_name": "Test Menu - Auto Sort",
        "parent_id": None,
        "menu_type": "menu",
        "route_path": "/test/auto-sort",
        "icon": "mdi-test",
        "is_enabled": True
    }

    response = requests.post(f"{BASE_URL}/admin/menus", json=menu_data)
    if response.status_code == 200:
        data = response.json()
        menu = data.get('data', {})
        print(f"[OK] Created menu with auto sort_order")
        print(f"  ID: {menu['id']}")
        print(f"  Name: {menu['menu_name']}")
        print(f"  Sort Order: {menu['sort_order']}")
        return menu['id']
    else:
        print(f"[ERROR] Failed to create menu: {response.status_code}")
        print(response.text)
        return None


def test_update_single_sort(menu_id):
    """测试单个菜单排序更新"""
    print_section("Test 3: Update Single Menu Sort Order")

    if not menu_id:
        print("[SKIP] No menu ID provided")
        return

    sort_data = {"sort_order": 999}

    response = requests.put(f"{BASE_URL}/admin/menus/{menu_id}/sort", json=sort_data)
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Updated menu sort order")
        print(f"  Menu ID: {data['data']['id']}")
        print(f"  New Sort Order: {data['data']['sort_order']}")
    else:
        print(f"[ERROR] Failed to update sort: {response.status_code}")
        print(response.text)


def test_batch_sort_update():
    """测试批量排序更新"""
    print_section("Test 4: Batch Update Menu Sort Orders")

    # 获取前3个菜单
    response = requests.get(f"{BASE_URL}/admin/menus")
    if response.status_code != 200:
        print("[ERROR] Failed to get menus for batch test")
        return

    data = response.json()
    menus = data.get('data', [])[:3]

    if len(menus) < 3:
        print("[SKIP] Not enough menus for batch test")
        return

    # 准备批量更新数据
    updates = [
        {"id": menus[0]['id'], "sort_order": 100},
        {"id": menus[1]['id'], "sort_order": 200},
        {"id": menus[2]['id'], "sort_order": 300}
    ]

    batch_data = {"updates": updates}

    response = requests.put(f"{BASE_URL}/admin/menus/batch-sort", json=batch_data)
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] {data['message']}")
        for update in updates:
            print(f"  Menu ID {update['id']} -> Sort Order {update['sort_order']}")
    else:
        print(f"[ERROR] Failed to batch update: {response.status_code}")
        print(response.text)


def test_reorder_menus():
    """测试自动重排序"""
    print_section("Test 5: Reorder Menus (Auto Redistribute)")

    response = requests.post(f"{BASE_URL}/admin/menus/reorder")
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] {data['message']}")
        print(f"  Reordered Count: {data['data']['count']}")
        print(f"  Parent ID: {data['data']['parent_id']}")
    else:
        print(f"[ERROR] Failed to reorder: {response.status_code}")
        print(response.text)


def test_validation():
    """测试排序值校验"""
    print_section("Test 6: Validation - Negative Sort Order")

    # 尝试设置负数排序值
    sort_data = {"sort_order": -10}

    response = requests.put(f"{BASE_URL}/admin/menus/1/sort", json=sort_data)
    if response.status_code == 422:
        print("[OK] Validation works - rejected negative sort_order")
        print(f"  Error: {response.json()}")
    else:
        print(f"[UNEXPECTED] Expected 422, got {response.status_code}")


def cleanup_test_menu(menu_id):
    """清理测试菜单"""
    print_section("Cleanup: Delete Test Menu")

    if not menu_id:
        print("[SKIP] No menu to cleanup")
        return

    response = requests.delete(f"{BASE_URL}/admin/menus/{menu_id}")
    if response.status_code == 200:
        print(f"[OK] Deleted test menu ID: {menu_id}")
    else:
        print(f"[WARNING] Failed to delete test menu: {response.status_code}")


def main():
    """主测试流程"""
    print("=" * 60)
    print("  Menu Sort API Test Suite")
    print("  Task #37 - Menu Sort Field Processing")
    print("=" * 60)

    try:
        # Test 1: 获取菜单列表
        test_get_menus()

        # Test 2: 创建菜单（自动排序）
        test_menu_id = test_create_menu()

        # Test 3: 单个菜单排序更新
        test_update_single_sort(test_menu_id)

        # Test 4: 批量排序更新
        test_batch_sort_update()

        # Test 5: 自动重排序
        test_reorder_menus()

        # Test 6: 校验测试
        test_validation()

        # Cleanup
        cleanup_test_menu(test_menu_id)

        print("\n" + "=" * 60)
        print("  [SUCCESS] All tests completed")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Cannot connect to API server")
        print("Please ensure the FastAPI server is running on http://localhost:8000")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
