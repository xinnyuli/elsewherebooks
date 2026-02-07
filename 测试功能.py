#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Elsewhere Books 记账本 - 自动化功能测试脚本

测试涵盖：
1. 数据服务（读写销售记录、店长管理）
2. 定价引擎（各种情况的价格计算）
3. 汇率服务（汇率获取和缓存）
4. 会员/非会员购买逻辑
5. 数据导出功能

运行方式：
  python 测试功能.py

或者测试单个模块：
  python 测试功能.py DataService
"""

import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime

# 添加当前目录到path
sys.path.insert(0, str(Path(__file__).parent))

from book_price_gui import (
    VintageConfig, DataService, PricingEngine, 
    ExchangeRateService
)

class TestResult:
    """测试结果收集器"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def assert_equal(self, actual, expected, test_name):
        """断言相等"""
        if actual == expected:
            self.passed += 1
            print(f"  ✓ {test_name}")
            return True
        else:
            self.failed += 1
            error = f"  ✗ {test_name}\n    期望: {expected}\n    实际: {actual}"
            print(error)
            self.errors.append(error)
            return False
    
    def assert_true(self, condition, test_name):
        """断言为真"""
        return self.assert_equal(condition, True, test_name)
    
    def assert_near(self, actual, expected, tolerance, test_name):
        """断言近似相等（用于浮点数）"""
        if abs(actual - expected) <= tolerance:
            self.passed += 1
            print(f"  ✓ {test_name}")
            return True
        else:
            self.failed += 1
            error = f"  ✗ {test_name}\n    期望: {expected} (±{tolerance})\n    实际: {actual}"
            print(error)
            self.errors.append(error)
            return False
    
    def summary(self):
        """打印总结"""
        total = self.passed + self.failed
        print("\n" + "="*60)
        print(f"测试完成: {total} 个测试")
        print(f"✓ 通过: {self.passed}")
        print(f"✗ 失败: {self.failed}")
        if self.failed > 0:
            print("\n失败的测试:")
            for error in self.errors:
                print(error)
        print("="*60)
        return self.failed == 0


def test_data_service():
    """测试数据服务"""
    print("\n【测试 DataService】")
    result = TestResult()
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # 临时修改配置
        orig_sales = VintageConfig.SALES_FILE
        orig_managers = VintageConfig.MANAGERS_FILE
        
        VintageConfig.SALES_FILE = tmppath / "sales.json"
        VintageConfig.MANAGERS_FILE = tmppath / "managers.json"
        
        try:
            service = DataService()
            
            # 测试初始化
            result.assert_true(VintageConfig.SALES_FILE.exists(), "销售文件自动创建")
            result.assert_true(VintageConfig.MANAGERS_FILE.exists(), "店长文件自动创建")
            
            # 测试保存销售
            books = [
                {"title": "测试书1", "category": "文学", "manager": "Kelly", 
                 "member_price": 10.0, "standard_price": 11.0, "final_price": 10.0},
                {"title": "测试书2", "category": "历史", "manager": "Kelly",
                 "member_price": 20.0, "standard_price": 22.0, "final_price": 20.0}
            ]
            success = service.save_sale(books, 30.0, 33.0, "member", 30.0)
            result.assert_true(success, "保存会员购买记录")
            
            # 测试非会员购买
            success = service.save_sale(books, 30.0, 33.0, "standard", 33.0)
            result.assert_true(success, "保存非会员购买记录")
            
            # 测试读取
            records = service.get_all_sales()
            result.assert_equal(len(records), 2, "读取保存的记录")
            result.assert_equal(records[0]["sale_type"], "member", "会员购买类型")
            result.assert_equal(records[1]["sale_type"], "standard", "非会员购买类型")
            result.assert_equal(records[0]["actual_revenue"], 30.0, "会员实际收入")
            result.assert_equal(records[1]["actual_revenue"], 33.0, "非会员实际收入")
            
            # 测试店长管理
            managers = service.get_managers()
            result.assert_true("Kelly" in managers, "默认店长存在")
            
            service.add_manager("Test Manager")
            managers = service.get_managers()
            result.assert_true("Test Manager" in managers, "添加新店长")
            
        finally:
            # 恢复原配置
            VintageConfig.SALES_FILE = orig_sales
            VintageConfig.MANAGERS_FILE = orig_managers
    
    return result


def test_pricing_engine():
    """测试定价引擎"""
    print("\n【测试 PricingEngine】")
    result = TestResult()
    
    # 模拟汇率
    rates = {"JPY": 100.0, "CNY": 5.0, "AUD": 1.0}
    
    # 测试1: 新书JPY 1000
    m, s = PricingEngine.calculate(1000, "JPY", False, False, False, rates)
    # 公式: base = (1000 * 1.15) / 100 = 11.5
    #       standard = 11.5 * 5 * 0.3 = 17.25
    result.assert_near(m, 11.5, 0.01, "新书JPY会员价")
    result.assert_near(s, 17.25, 0.01, "新书JPY标准价")
    result.assert_true(s > m, "标准价 > 会员价")
    
    # 测试2: 推荐书JPY 1000
    m, s = PricingEngine.calculate(1000, "JPY", True, False, False, rates)
    # 推荐书: member = 11.5 * 0.9 = 10.35
    #        standard = 11.5 (无coefficient)
    result.assert_near(m, 10.35, 0.01, "推荐书JPY会员价 (90%折扣)")
    result.assert_near(s, 11.5, 0.01, "推荐书JPY标准价")
    result.assert_true(s > m, "推荐书: 标准价 > 会员价")
    
    # 测试3: 二手书AUD 10
    m, s = PricingEngine.calculate(10, "AUD", False, True, False, rates)
    result.assert_equal(m, 10.0, "二手书会员价 = 原价")
    result.assert_equal(s, 10.0, "二手书标准价 = 原价")
    
    # 测试4: 书阁租赁AUD 5
    m, s = PricingEngine.calculate(5, "AUD", False, False, True, rates)
    result.assert_equal(m, 5.0, "书阁租赁会员价 = 原价")
    result.assert_equal(s, 5.0, "书阁租赁标准价 = 原价")
    
    # 测试5: 人民币CNY 50
    m, s = PricingEngine.calculate(50, "CNY", False, False, False, rates)
    # base = (50 * 1.15) / 5 = 11.5
    result.assert_near(m, 11.5, 0.01, "新书CNY会员价")
    result.assert_true(s > m, "CNY: 标准价 > 会员价")
    
    # 测试6: 边界情况 - 价格为0
    m, s = PricingEngine.calculate(0, "AUD", False, False, False, rates)
    result.assert_equal(m, 0.0, "价格为0时会员价")
    result.assert_equal(s, 0.0, "价格为0时标准价")
    
    return result


def test_exchange_rate_service():
    """测试汇率服务"""
    print("\n【测试 ExchangeRateService】")
    result = TestResult()
    
    service = ExchangeRateService()
    
    # 测试初始状态
    result.assert_true(not service.has_rates(), "初始无汇率数据")
    
    # 测试模拟汇率（通过内部_rates设置）
    with service._lock:
        service._rates = {"JPY": 100.0, "CNY": 5.0, "AUD": 1.0}
    result.assert_true(service.has_rates(), "设置汇率后有数据")
    result.assert_equal(service.rates.get("JPY"), 100.0, "汇率JPY正确")
    
    print("  ℹ️  实际网络请求已跳过（需手动测试）")
    
    return result


def test_member_vs_standard():
    """测试会员/非会员购买逻辑"""
    print("\n【测试会员/非会员购买逻辑】")
    result = TestResult()
    
    rates = {"JPY": 100.0, "CNY": 5.0, "AUD": 1.0}
    
    # 准备测试数据（都是新书）
    books_data = [
        {"price": 1000, "currency": "JPY", "is_recommend": False, "is_used": False, "is_rental": False},
        {"price": 10, "currency": "AUD", "is_recommend": False, "is_used": False, "is_rental": False},
    ]
    
    total_member = 0.0
    total_standard = 0.0
    
    for book in books_data:
        m, s = PricingEngine.calculate(
            book["price"], book["currency"], 
            book["is_recommend"], book["is_used"], 
            book["is_rental"], rates
        )
        total_member += m
        total_standard += s
    
    # 验证会员总价 < 标准总价（新书应该如此）
    result.assert_true(total_member < total_standard, "新书：会员总价 < 标准总价")
    
    print(f"  💰 会员总价: ${total_member:.2f}")
    print(f"  💰 标准总价: ${total_standard:.2f}")
    print(f"  📊 差价: ${total_standard - total_member:.2f}")
    
    # 测试二手书（应该相等）
    m2, s2 = PricingEngine.calculate(10, "AUD", False, True, False, rates)
    result.assert_equal(m2, s2, "二手书：会员价 = 标准价")
    
    return result


def test_edge_cases():
    """测试边界情况"""
    print("\n【测试边界情况】")
    result = TestResult()
    
    rates = {"JPY": 100.0, "CNY": 5.0, "AUD": 1.0}
    
    # 测试极小价格
    m, s = PricingEngine.calculate(0.01, "AUD", False, False, False, rates)
    result.assert_true(m > 0, "极小价格会员价有效")
    result.assert_true(s > m, "极小价格：标准价 > 会员价")
    
    # 测试极大价格
    m, s = PricingEngine.calculate(99999, "JPY", False, False, False, rates)
    result.assert_true(m > 1000, "极大价格会员价合理")
    result.assert_true(s > m, "极大价格：标准价 > 会员价")
    
    # 测试推荐书（会员享受折扣）
    m_normal, s_normal = PricingEngine.calculate(100, "AUD", False, False, False, rates)
    m_recommend, s_recommend = PricingEngine.calculate(100, "AUD", True, False, False, rates)
    result.assert_true(m_recommend < m_normal, "推荐书会员价有折扣")
    result.assert_near(m_recommend / m_normal, 0.9, 0.01, "推荐书会员价折扣90%")
    
    # 书阁不应该受推荐影响
    m2, s2 = PricingEngine.calculate(5, "AUD", True, False, True, rates)
    m3, s3 = PricingEngine.calculate(5, "AUD", False, False, True, rates)
    result.assert_equal(m2, m3, "书阁不受推荐标记影响")
    
    return result


def main():
    """主测试函数"""
    print("="*60)
    print("  📚 Elsewhere Books 记账本 - 功能测试")
    print("="*60)
    print(f"  Python版本: {sys.version.split()[0]}")
    print(f"  测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 运行所有测试
    test_modules = {
        "DataService": test_data_service,
        "PricingEngine": test_pricing_engine,
        "ExchangeRateService": test_exchange_rate_service,
        "MemberVsStandard": test_member_vs_standard,
        "EdgeCases": test_edge_cases
    }
    
    # 如果命令行指定了模块，只测试该模块
    if len(sys.argv) > 1:
        module_name = sys.argv[1]
        if module_name in test_modules:
            test_modules = {module_name: test_modules[module_name]}
        else:
            print(f"\n❌ 未知测试模块: {module_name}")
            print(f"可用模块: {', '.join(test_modules.keys())}")
            return False
    
    # 执行测试
    all_results = []
    for name, test_func in test_modules.items():
        try:
            result = test_func()
            all_results.append(result)
        except Exception as e:
            print(f"\n❌ 测试 {name} 时发生错误:")
            print(f"   {str(e)}")
            import traceback
            traceback.print_exc()
    
    # 合并结果
    total_result = TestResult()
    for r in all_results:
        total_result.passed += r.passed
        total_result.failed += r.failed
        total_result.errors.extend(r.errors)
    
    # 显示总结
    success = total_result.summary()
    
    if success:
        print("\n✅ 所有测试通过！")
        return True
    else:
        print("\n⚠️  部分测试失败，请检查上面的错误信息")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
