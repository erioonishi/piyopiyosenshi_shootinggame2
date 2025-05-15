import pygame  #ゲーム開発用ライブラリ
import sys  #sys.exit()でPythonプログラムを終了するため(絶対いる)
from game import Game

#main.pyはゲームお決まりの書き方なのですが…解説は下のほうにコメントで

# 初期化　(ここはpygameのお決まりの書き方→一番下に例を書いておく)
pygame.init()  #Pygame全体を初期化(これを呼ばないとPygameの機能が使えない
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))  #ウィンドウを作成して、その画面オブジェクトをscreenに保存
pygame.display.set_caption("ぴよぴよ戦士シューティングゲーム")  #タイトルバー
clock = pygame.time.Clock()  #フレームレート(1秒間に何回画面更新するか)を制御するClockオブジェクト

game = Game(screen, WIDTH, HEIGHT)  #画面やサイズを渡してGameクラスのインスタンスを作り、ゲーム全体を管理

# ここからメインループ!!
# ゲームループ(イベント処理 → 更新 → 描画のゲーム基本の書き方で下に流れ書いておく)
while True: #無限ループでゲームループを開始(ここがゲームの中心部分)

    for event in pygame.event.get():  #すべてのイベント(キー入力/マウス/タイマーイベントなど)を順番に取得して処理
        if event.type == pygame.QUIT:  #閉じるボタンが押されたら、Pygameを終了してPythonプログラムも終了(import sys)
            pygame.quit()
            sys.exit()

        if not game.game_over:  # ゲームオーバー時ではない
            game.handle_input(event)
        else:  # ゲームオーバー時でも入力処理
            game.handle_input(event)

    keys = pygame.key.get_pressed()  #今現在押されているキーの状態をまとめて取得(例えば、押しっぱなしの移動キーを感知)
    game.update(keys)  #ゲームの状態を更新(プレイヤーや弾・敵の移動、当たり判定など)キーの状態も渡す

    screen.fill((0, 0, 0))  #画面を黒で塗りつぶして一旦リセット(毎フレーム必須)
    game.draw()  #プレイヤー・弾・敵・スコアなどを現在の状態に応じて描画
    pygame.display.flip()  #画面に描画した内容を一気に反映し、画面の更新
    clock.tick(60)  #このループが1秒間に最大60回動くように制御(フレームレート60FPS)

'''
★pygame使用するときの初期化の書き方
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ゲームタイトル")
clock = pygame.time.Clock()
【説明】
pygame.init()(イニットinitialize（初期化する）)
→ これはPygameのすべての機能(ビデオ、オーディオなど)をまとめて初期化するためにほぼ必須
pygame.display.set_mode()
→ ゲームウィンドウを開かないと何も表示できないので、これはゲームを始める前提条件
pygame.display.set_caption()
→ ここは任意だが、ウィンドウの名前をつける
pygame.time.Clock()
→ これはフレームレート制御のためで、ループの速さを適切に保つため、必須
'''

'''
★イベント処理 → 状態更新 → 描画についての書き方
⑴イベント処理（入力やウィンドウ閉じるなどの検知）
【code】
for event in pygame.event.get():
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

    if not game.game_over:
        if event.type == ENEMY_SPAWN_EVENT:
            game.spawn_enemy()
        else:
            game.handle_input(event)
    else:
        game.handle_input(event)
【役割】
・キー入力とか
・敵を出現させるタイマーイベント
・ウィンドウ閉じる操作など
これらを受け取って処理
⑵状態更新(ゲームの内部データを進める)
【code】
keys = pygame.key.get_pressed()
game.update(keys)
【役割】
・プレイヤーが動く
・弾が進む
・敵が動く
・当たり判定する
というゲーム内の状態が変わる処理
⑶描画(画面に表示)
【code】
screen.fill((0, 0, 0))
game.draw()
pygame.display.flip()
【役割】
・背景クリア（fill）
    →これやらないと弾が1ピクセル上に移動したとしても、前の位置の弾の絵が残るって弾の軌跡がずっと線のように残る。
    1秒間にだいたい60回（60FPS）くらい画面を更新してるから毎回消そう(お絵描きアプリはまた逆に残すよ)
・プレイヤー・敵・弾などの描画（game.draw()）
・実際の画面に反映（flip()）
'''

'''
★コメントなしのcodeだけ必要な時
import pygame
import sys
from game import Game

# 初期化
pygame.init()
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("シューティングゲーム")
clock = pygame.time.Clock()

game = Game(screen, WIDTH, HEIGHT)

ENEMY_SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(ENEMY_SPAWN_EVENT, 4000)

# ゲームループ
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if not game.game_over:  # ゲームオーバー時ではない
            if event.type == ENEMY_SPAWN_EVENT:
                game.spawn_enemy()
            else:
                game.handle_input(event)
        else:  # ゲームオーバー時でも入力処理
            game.handle_input(event)

    keys = pygame.key.get_pressed()
    game.update(keys)

    screen.fill((0, 0, 0))
    game.draw()
    pygame.display.flip()
    clock.tick(60)
'''