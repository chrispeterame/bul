import sys
sys.path.insert(0, r'f:\新建文件夹\123')

import time
from game import GameState

def test_game_generation():
    test_sizes = [4, 5, 6, 7, 8]
    
    print("=" * 50)
    print("测试游戏生成性能")
    print("=" * 50)
    
    for size in test_sizes:
        print(f"\n测试 {size}x{size} 游戏...")
        
        start_time = time.time()
        try:
            game = GameState(size)
            elapsed = time.time() - start_time
            
            print(f"  ✓ 生成成功! 耗时: {elapsed:.2f}秒")
            print(f"    牛位置: {game.cows}")
            
            color_counts = {}
            for r in range(size):
                for c in range(size):
                    color = game.colors[r][c]
                    color_counts[color] = color_counts.get(color, 0) + 1
            
            print(f"    颜色分布: {dict(sorted(color_counts.items()))}")
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"  ✗ 生成失败! 耗时: {elapsed:.2f}秒")
            print(f"    错误: {e}")
    
    print("\n" + "=" * 50)
    print("多轮测试稳定性验证")
    print("=" * 50)
    
    for size in test_sizes:
        print(f"\n{size}x{size} 连续测试5轮:")
        success_count = 0
        total_time = 0
        
        for i in range(5):
            start_time = time.time()
            try:
                game = GameState(size)
                elapsed = time.time() - start_time
                total_time += elapsed
                success_count += 1
                print(f"  轮次 {i+1}: ✓ {elapsed:.2f}秒")
            except Exception as e:
                elapsed = time.time() - start_time
                print(f"  轮次 {i+1}: ✗ {elapsed:.2f}秒 - {str(e)[:50]}")
        
        if success_count == 5:
            avg_time = total_time / 5
            print(f"  全部成功! 平均耗时: {avg_time:.2f}秒")
        else:
            print(f"  成功率: {success_count}/5")

if __name__ == "__main__":
    test_game_generation()
