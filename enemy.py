import pygame
import random  #敵の初期位置をランダムに決める

class Enemy(pygame.sprite.Sprite):  #Enemyクラスを定義(pygame.sprite.Sprite)を継承してPygameのスプライト機能使える

    def __init__(self, screen_width):  #コンストラクタ(初期化メソッド)引数として画面の横幅(screen_width)をもらい、ランダム位置決定

        super().__init__()  #親クラス(pygame.sprite.Sprite)の初期化を呼ぶ(スプライトとして正しく動かすための決まり)
        self.image = pygame.image.load("assets/images/enemy.png").convert_alpha()  #.convert_alpha()は透過処理を有効にする
        self.image = pygame.transform.scale(self.image, (40, 40))  #必要に応じてサイズ調整(読み込んだ画像を40×40ピクセルにリサイズ)
        self.rect = self.image.get_rect()  #このrectは位置(x, y)やサイズ(幅・高さ)を持つ、当たり判定や位置制御のためのオブジェクト
        self.rect.x = random.randint(0, screen_width - self.rect.width)  #x座標をランダムで決めて0から画面幅-敵の幅の範囲で選び、敵が画面からはみ出さない
        self.rect.y = -self.rect.height  #y座標は、画面の上の外側にセット
        self.speed = 2  #2ピクセルずつおちる速度（必要に応じて調整）

    def update(self):  #更新処理
        self.rect.y += self.speed  #y座標をself.speedだけ増やすことで、敵が下方向に移動
        return self.rect.top > 600  #画面外に出たらTrue → Trueは呼び出し側で「消すか残すか」の判定
'''    
★敵を描画する場合(今回は手書きのイラストを使った)
import pygame
import random

class Enemy(pygame.sprite.Sprite):
    def __init__(self, screen_width):
        super().__init__()
        self.image = pygame.Surface((40, 30))
        self.image.fill((255, 0, 0))
        x = random.randint(0, screen_width - 40)
        self.rect = self.image.get_rect(topleft=(x, 0))
        self.speed = 1  # ゆっくりにする

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > 600:
            return True  # 到達したらTrue（GameOverトリガー）
        return False
'''

'''
★Pygameのスプライト機能とは
オブジェクトの画像・位置を持ち、グループでまとめて便利に操作できるもの
【スプライトの特徴】
pygame.sprite.Spriteクラスを継承して作る
各スプライトは
・image属性（見た目）
・rect属性(レクト)は位置やサイズを持つ
・当たり判定などが簡単にできる
・複数のスプライトをグループ(pygame.sprite.Groupなど)にまとめて
〇一括で更新 (update())
〇一括で描画 (draw())
〇衝突判定 (groupcollide(), spritecollide())
ができる
【今回の使い方】
⑴Enemyクラスがスプライト
class Enemy(pygame.sprite.Sprite):
このようにスプライトクラスとして作られていて、…image見た目、…rectで位置・サイズをセット
⑵Gameクラス側で「スプライトグループ」を作る
self.enemy_group = pygame.sprite.Group()
self.bullet_group = pygame.sprite.Group()というように複数の敵や弾をグループ化
これにより、描画・更新・当たり判定(敵と弾が当たればまとめて消す)をまとめて行う
スプライトがないと弾・敵を1個ずつfor文で回して管理しないといけない
'''

'''
★screen_widthはどこからもらってるか
main.pyの
WIDTH, HEIGHT = 600, 600
game = Game(screen, WIDTH, HEIGHT)から
Gameクラスの__init__で
def __init__(self, screen, width, height):
    self.WIDTH = width  ← これで保存しておく
Gameクラスのspawn_enemy()で
enemy = Enemy(self.WIDTH)
これでEnemyがscreen_width=600をもらえる
'''

'''
★__init__とは(_init_ではだめ)
インスタンスを作るときに最初に呼ばれる初期化メソッド
〈例〉enemy = Enemy(screen_width)
とすると、
⑴Enemyクラスの
⑵__init__()メソッドが実行されて
⑶そのオブジェクトが作られるという流れ
今回のcodeで見てみると
この__init__の目的は
⑴敵スプライトを1体作る
⑵画像や位置・サイズを設定する
⑶画面上側の外から落ちてくるようにする
⑷という初期化を1発で済ませる
'''

'''
★.convert_alpha()の透過の必要性
⑴描画を速くするため
・Pygameの画面は「特定のピクセルフォーマット」で動いている
・読み込んだ画像はそのままだと遅くて非効率的なので、Pygameの画面に最適化する必要がある
・convert_alpha()を使うと、その画像がPygameの画面フォーマットに合わせて高速化される
⑵透明部分を正しく表示するため
・.pngなど、透明な背景を持つ画像を読み込むときは、透明部分をちゃんと扱う必要がある
・convert_alpha()は、透明情報（アルファチャンネル）を保持してくれる
⑶使わなかったら
・背景が透明じゃなく真っ黒とか変な表示になる
・処理が重くなる（パフォーマンス低下）
'''

'''
★rectとは
Pygameでは、画像(Surface)を「どこに表示するか」や「当たり判定」を管理するために、Rect(矩形：くけい)オブジェクトを使う
このRectは 位置と大きさの情報をまとめて持っている便利なもの
【Rectの主な中身】
・x, y（左上の座標）
・width, height（幅と高さ）
・top, bottom, left, right, centerx, centery など、位置を簡単に参照できる属性もある
'''

'''
★selfとは
selfはそのクラスの「自分自身」を表すもの
プレイヤーの「名前」
プレイヤーの「HP」
プレイヤーの「位置」
このプレイヤー自身をcodeの中で表すのがself
・self.imageはこのプレイヤー自身が持っている画像
・self.rectはこのプレイヤー自身が持っている位置情報
selfがないと一時的に読み込むだけで、このプレイヤーが持ってるものとは認識されない
self.image = ... とすることで、
そのインスタンス（自分自身）に保存することができる
クラスの中の関数(メソッド)は、自分の持ち物を定義するときは必ずselfを付ける
'''

'''
★コメントなしのcodeだけ必要な時
import pygame
import random

class Enemy(pygame.sprite.Sprite):
    def __init__(self, screen_width):
        super().__init__()
        self.image = pygame.image.load("assets/images/enemy.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (40, 40))  # 必要に応じてサイズ調整
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, screen_width - self.rect.width)
        self.rect.y = -self.rect.height
        self.speed = 2  # おちる速度（必要に応じて調整）

    def update(self):
        self.rect.y += self.speed
        return self.rect.top > 600  # 画面外に出たら True（修正：画面高さに合わせて）

        
'''