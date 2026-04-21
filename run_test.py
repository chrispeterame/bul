import sys
sys.path.insert(0, r'f:\新建文件夹\123')
import time
from game import GameState

def main():
    print("=" * 60)
    print("Find The Cows Game - All Difficulties Test")
    print("=" * 60)
    
    all_sizes = [4, 5, 6, 7, 8]
    results = {}
    
    for size in all_sizes:
        print("\n[" + str(size) + "x" + str(size) + "] Testing...")
        sys.stdout.flush()
        
        start_time = time.time()
        try:
            game = GameState(size)
            elapsed = time.time() - start_time
            
            color_counts = {}
            for r in range(size):
                for c in range(size):
                    color = game.colors[r][c]
                    color_counts[color] = color_counts.get(color, 0) + 1
            
            results[size] = {
                'success': True,
                'time': elapsed,
                'color_counts': color_counts,
                'cows': game.cows
            }
            
            print("  OK! Time: " + str(round(elapsed, 2)) + "s")
            print("  Color distribution: " + str(dict(sorted(color_counts.items()))))
            
        except Exception as e:
            elapsed = time.time() - start_time
            results[size] = {
                'success': False,
                'time': elapsed,
                'error': str(e)
            }
            print("  FAIL! Time: " + str(round(elapsed, 2)) + "s")
            print("  Error: " + str(e))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    for size in all_sizes:
        r = results[size]
        if r['success']:
            print("  " + str(size) + "x" + str(size) + ": OK (" + str(round(r['time'], 2)) + "s)")
        else:
            print("  " + str(size) + "x" + str(size) + ": FAIL - " + str(r['error']))
    
    print("\n" + "=" * 60)
    print("Stability Test - 3 rounds each")
    print("=" * 60)
    
    for size in [6, 7, 8]:
        print("\n[" + str(size) + "x" + str(size) + "] 3 rounds:")
        success_count = 0
        total_time = 0
        
        for i in range(3):
            start = time.time()
            try:
                g = GameState(size)
                t = time.time() - start
                total_time += t
                success_count += 1
                print("  Round " + str(i+1) + ": OK (" + str(round(t, 2)) + "s)")
            except Exception as e:
                t = time.time() - start
                print("  Round " + str(i+1) + ": FAIL - " + str(e)[:50])
        
        if success_count == 3:
            avg = total_time / 3
            print("  All OK! Avg time: " + str(round(avg, 2)) + "s")
        else:
            print("  Success rate: " + str(success_count) + "/3")

if __name__ == "__main__":
    main()
