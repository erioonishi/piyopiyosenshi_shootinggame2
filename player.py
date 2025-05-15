import pygame
from bullet import Bullet  #弾を作るために必要

class Player(pygame.sprite.Sprite):  #Playerクラスを定義(pygame.sprite.Sprite)を継承し、Pygameのスプライト機能(描画やグループ管理)が使える
    def __init__(self, screen_width, screen_height):  #Playerクラスのコンストラクタ(初期化関数)引数として画面サイズを受け取り、後で自分の位置を決める
        super().__init__()  #親クラス(pygame.sprite.Sprite)の初期化を呼ぶ(スプライトとして正しく動かすための決まり)

        # 画像を読み込んで使うように変更
        self.image = pygame.image.load("assets/images/piyopiyo2.png").convert_alpha()  #convert_alpha()透明部分をきれいに表示
        self.image = pygame.transform.scale(self.image, (60, 60))  #読み込んだ画像を60×60ピクセルにサイズ変更

        self.rect = self.image.get_rect(center=(screen_width // 2, screen_height - 60))  #画像の当たり判定エリア(rect)を設定画面の中央下あたりに配置(center=(画面の横半分, 画面の高さ-60))self.rectは「位置」と「当たり判定」に使用
        self.speed = 5  #プレイヤーの移動速度を5ピクセルに設定
        self.screen_width = screen_width  #画面の幅を保存しておき、後で「画面の端で止まる」処理に使う

    def update(self, keys):  #毎フレーム呼ばれる更新メソッドで、keysはpygame.key.get_pressed()の結果を受け取る
        if keys[pygame.K_LEFT]:  #左キーが押されてたら左に移動
            self.rect.x -= self.speed  #speedの分だけ左へ
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        self.rect.x = max(0, min(self.screen_width - self.rect.width, self.rect.x))  #画面端で止める処理画面左は0、右端は 画面の幅 - プレイヤーの幅 で制限して、画面外に出ない

    def shoot(self):  #弾を撃つときに呼び出す関数で現在のプレイヤーの中央上部から弾を出すようにしている
        return Bullet(self.rect.centerx, self.rect.top)  #新しい弾を作り、呼び出し元に返す

'''
★描画する場合(今回は手書きのイラストを使った)
import pygame
from bullet import Bullet

class Player(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height):
        super().__init__()
        self.image = pygame.Surface((50, 40))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(center=(screen_width // 2, screen_height - 60))
        self.speed = 5
        self.screen_width = screen_width

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        self.rect.x = max(0, min(self.screen_width - self.rect.width, self.rect.x))

    def shoot(self):
        return Bullet(self.rect.centerx, self.rect.top)
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
★rectとは
Pygameでは、画像(Surface)を「どこに表示するか」や「当たり判定」を管理するために、Rect(矩形：くけい)オブジェクトを使う
このRectは 位置と大きさの情報をまとめて持っている便利なもの
【Rectの主な中身】
・x, y（左上の座標）
・width, height（幅と高さ）
・top, bottom, left, right, centerx, centery など、位置を簡単に参照できる属性もある
<例>
self.rect = self.image.get_rect(center=(screen_width // 2, screen_height - 60))
⑴self.image.get_rect()は、画像のサイズと同じ幅・高さのRectを作る。この時点では(0, 0)にある。
⑵center=(screen_width // 2, screen_height - 60) によって、画面の横の真ん中、下の方に配置
'''

'''
★コメントなしのcodeだけ必要な時
import pygame
from bullet import Bullet

class Player(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height):
        super().__init__()

        # 画像を読み込んで使うように変更
        self.image = pygame.image.load("assets/images/piyopiyo2.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))  # サイズ調整はここで

        self.rect = self.image.get_rect(center=(screen_width // 2, screen_height - 60))
        self.speed = 5
        self.screen_width = screen_width

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        self.rect.x = max(0, min(self.screen_width - self.rect.width, self.rect.x))

    def shoot(self):
        return Bullet(self.rect.centerx, self.rect.top)

'''