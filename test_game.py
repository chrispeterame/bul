from game import GameState

for n in range(4, 11):
    print(f"Testing n={n}...")
    try:
        game = GameState(n)
        print(f"  ✓ Game created successfully for n={n}")
        print(f"  - Cows: {game.cows}")
        print(f"  - Colors generated: {len(game.colors)}x{len(game.colors[0])}")
    except Exception as e:
        print(f"  ✗ Failed for n={n}: {e}")
