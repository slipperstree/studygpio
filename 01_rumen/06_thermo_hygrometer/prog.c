#include <wiringPi.h>
#include <unistd.h>
#include <time.h>

// 定义单个数码管各段led对应的GPIO口
// 使用命令 "gpio readall" 来获取当前pi版本对应的各引脚的wiringPi和BCM的编号
// 再本程序中应该使用wiringPi编号
// 我的pi2 Mode B执行结果如下：（wPi列就是wiringPi编号）
// 之前Python版本的代码使用的是BCM编号，所以在不改变硬件接线的情况下，我们需要把原来BCM编号改成对应的wiringPi编号。
/* 
 +-----+-----+---------+------+---+---Pi 2---+---+------+---------+-----+-----+
 | BCM | wPi |   Name  | Mode | V | Physical | V | Mode | Name    | wPi | BCM |
 +-----+-----+---------+------+---+----++----+---+------+---------+-----+-----+
 |     |     |    3.3v |      |   |  1 || 2  |   |      | 5v      |     |     |
 |   2 |   8 |   SDA.1 |   IN | 1 |  3 || 4  |   |      | 5V      |     |     |
 |   3 |   9 |   SCL.1 |   IN | 1 |  5 || 6  |   |      | 0v      |     |     |
 |   4 |   7 | GPIO. 7 |   IN | 1 |  7 || 8  | 1 | ALT0 | TxD     | 15  | 14  |
 |     |     |      0v |      |   |  9 || 10 | 1 | ALT0 | RxD     | 16  | 15  |
 |  17 |   0 | GPIO. 0 |  OUT | 0 | 11 || 12 | 0 | IN   | GPIO. 1 | 1   | 18  |
 |  27 |   2 | GPIO. 2 |   IN | 0 | 13 || 14 |   |      | 0v      |     |     |
 |  22 |   3 | GPIO. 3 |   IN | 0 | 15 || 16 | 0 | IN   | GPIO. 4 | 4   | 23  |
 |     |     |    3.3v |      |   | 17 || 18 | 0 | IN   | GPIO. 5 | 5   | 24  |
 |  10 |  12 |    MOSI |   IN | 0 | 19 || 20 |   |      | 0v      |     |     |
 |   9 |  13 |    MISO |   IN | 0 | 21 || 22 | 0 | IN   | GPIO. 6 | 6   | 25  |
 |  11 |  14 |    SCLK |   IN | 0 | 23 || 24 | 1 | IN   | CE0     | 10  | 8   |
 |     |     |      0v |      |   | 25 || 26 | 1 | IN   | CE1     | 11  | 7   |
 |   0 |  30 |   SDA.0 |   IN | 1 | 27 || 28 | 1 | IN   | SCL.0   | 31  | 1   |
 |   5 |  21 | GPIO.21 |   IN | 1 | 29 || 30 |   |      | 0v      |     |     |
 |   6 |  22 | GPIO.22 |   IN | 1 | 31 || 32 | 0 | IN   | GPIO.26 | 26  | 12  |
 |  13 |  23 | GPIO.23 |   IN | 0 | 33 || 34 |   |      | 0v      |     |     |
 |  19 |  24 | GPIO.24 |   IN | 0 | 35 || 36 | 0 | IN   | GPIO.27 | 27  | 16  |
 |  26 |  25 | GPIO.25 |   IN | 0 | 37 || 38 | 0 | IN   | GPIO.28 | 28  | 20  |
 |     |     |      0v |      |   | 39 || 40 | 0 | IN   | GPIO.29 | 29  | 21  |
 +-----+-----+---------+------+---+----++----+---+------+---------+-----+-----+
 | BCM | wPi |   Name  | Mode | V | Physical | V | Mode | Name    | wPi | BCM |
 +-----+-----+---------+------+---+---Pi 2---+---+------+---------+-----+-----+
*/

#define LED_A 25 //BCM：26
#define LED_B 24 //BCM：19
#define LED_C 23 //BCM：13
#define LED_D 22 //BCM：6
#define LED_E 21 //BCM：5
#define LED_F 14 //BCM：11
#define LED_G 13 //BCM：9
#define LED_DP 12 //BCM：10

// 定义1到4号数码管阳极对应的GPIO口
#define DIGIT1 26 //BCM：12
#define DIGIT2 27 //BCM：16
#define DIGIT3 28 //BCM：20
#define DIGIT4 29 //BCM：21

// 定义按钮输入的GPIO口
#define btn 2 //BCM：27

#define FALSE 0
#define TRUE  1

#define t 5000 //数码管动态扫描的延时长度（单位um微秒，1000um＝1ms，1000ms＝1s）

// ####################################################################################
// 一次完整的数据传输为40bit,高位先出。
// 数据格式:8bit湿度整数数据+8bit湿度小数数据
//          +8bi温度整数数据+8bit温度小数数据
//          +8bit校验和
//          校验和数据等于
//             “8bit湿度整数数据+8bit湿度小数数据+8bi温度整数数据+8bit温度小数数据”
//             所得结果的末8位。
// 温度数据变量
char wendu = 0;
// 湿度数据变量
char shidu = 0;

// 定义温湿度计的data口连接的gpio口
#define DATA 7 //BCM: 4

// 根据DHT11的硬件时序图定义各种延时所需的时间间隔(单位：微秒)
// 总线空闲状态为高电平,主机把总线拉低等待DHT11响应,
// 主机把总线拉低必须大于18毫秒,保证DHT11能检测到起始信号。
#define t_pi_start 18000

// 主机发送开始信号结束后,延时等待20-40us后, 读取DHT11的响应信号,
// 主机发送开始信号后,可以切换到输入模式,或者输出高电平均可, 总线由上拉电阻拉高。
#define t_pi_start_wait 40

// DHT11接收到主机的开始信号后,等待主机开始信号结束,然后发送80us低电平响应信号。
// 总线为低电平,说明DHT11发送响应信号,DHT11发送响应信号后,再把总线拉高80us,
#define t_dht11_start_resp 80

// 准备发送数据,每一bit数据都以50us低电平时隙开始,高电平的长短定了数据位是0还是1。
#define t_dht11_data_head 50
#define t_dht11_data_0 26
#define t_dht11_data_1 70

// 如果读取响应信号为高电平,则DHT11没有响应,请检查线路是否连接正常。
// 当最后一bit数据传送完毕后，DHT11拉低总线50us,随后总线由上拉电阻拉高进入空闲状态。

// ####################################################################################

// 指定no(1-4)号数码管显示数字num(0-9)，第三个参数是显示不显示小数点（1/0）
void showDigit(int no, int num, int showDotPoint);

// 读取DHT11的温度湿度数据
void readDHT11();

time_t now;
struct tm *tm_now;

int main (void) {
  wiringPiSetup () ;

  pinMode (LED_A, OUTPUT) ;
  pinMode (LED_B, OUTPUT) ;
  pinMode (LED_C, OUTPUT) ;
  pinMode (LED_D, OUTPUT) ;
  pinMode (LED_E, OUTPUT) ;
  pinMode (LED_F, OUTPUT) ;
  pinMode (LED_G, OUTPUT) ;
  pinMode (LED_DP, OUTPUT) ;

  pinMode (DIGIT1, OUTPUT) ;
  pinMode (DIGIT2, OUTPUT) ;
  pinMode (DIGIT3, OUTPUT) ;
  pinMode (DIGIT4, OUTPUT) ;

  pinMode (btn, INPUT) ;
  pullUpDnControl (btn, PUD_UP) ;

  pinMode (DATA, OUTPUT) ;

  digitalWrite (DIGIT1, HIGH) ;
  digitalWrite (DIGIT2, HIGH) ;
  digitalWrite (DIGIT3, HIGH) ;
  digitalWrite (DIGIT4, HIGH) ;

  for (; ; )
  {
    time(&now);
    tm_now=localtime(&now);

    // 按钮按下时显示日期，否则显示时间
    // 为了区别左右的数字，让第二个数码管的小数点显示出来
    //（本来应该是一个冒号，我们这个数码管没有，就用小数点代替了）
    if (digitalRead(btn) == HIGH) {
      usleep(t);
      showDigit(1, tm_now->tm_hour / 10, FALSE);
      usleep(t);
      showDigit(2, tm_now->tm_hour % 10, TRUE);
      usleep(t);
      showDigit(3, tm_now->tm_min / 10, FALSE);
      usleep(t);
      showDigit(4, tm_now->tm_min % 10, FALSE);
    } else {
      // 取得的月份和日期都是从0开始的，所以显示前需要加1
      usleep(t);
      showDigit(1, (tm_now->tm_mon+1) / 10, FALSE);
      usleep(t);
      showDigit(2, (tm_now->tm_mon+1) % 10, TRUE);
      usleep(t);
      showDigit(3, (tm_now->tm_mday+1) / 10, FALSE);
      usleep(t);
      showDigit(4, (tm_now->tm_mday+1) % 10, FALSE);
    }
  }
  return 0 ;
}

void readDHT11() {
  
}

void showDigit(int no, int num, int showDotPoint) {
  // 先将正极拉低，关掉显示
  digitalWrite (DIGIT1, LOW) ;
  digitalWrite (DIGIT2, LOW) ;
  digitalWrite (DIGIT3, LOW) ;
  digitalWrite (DIGIT4, LOW) ;

  if (num == 0) {
    digitalWrite (LED_A, LOW) ;
    digitalWrite (LED_B, LOW) ;
    digitalWrite (LED_C, LOW) ;
    digitalWrite (LED_D, LOW) ;
    digitalWrite (LED_E, LOW) ;
    digitalWrite (LED_F, LOW) ;
    digitalWrite (LED_G, HIGH) ;
  } else if (num == 1) {
    digitalWrite (LED_A, HIGH) ;
    digitalWrite (LED_B, LOW) ;
    digitalWrite (LED_C, LOW) ;
    digitalWrite (LED_D, HIGH) ;
    digitalWrite (LED_E, HIGH) ;
    digitalWrite (LED_F, HIGH) ;
    digitalWrite (LED_G, HIGH) ;
  } else if (num == 2) {
    digitalWrite (LED_A, LOW) ;
    digitalWrite (LED_B, LOW) ;
    digitalWrite (LED_C, HIGH) ;
    digitalWrite (LED_D, LOW) ;
    digitalWrite (LED_E, LOW) ;
    digitalWrite (LED_F, HIGH) ;
    digitalWrite (LED_G, LOW) ;
  } else if (num == 3) {
    digitalWrite (LED_A, LOW) ;
    digitalWrite (LED_B, LOW) ;
    digitalWrite (LED_C, LOW) ;
    digitalWrite (LED_D, LOW) ;
    digitalWrite (LED_E, HIGH) ;
    digitalWrite (LED_F, HIGH) ;
    digitalWrite (LED_G, LOW) ;
  } else if (num == 4) {
    digitalWrite (LED_A, HIGH) ;
    digitalWrite (LED_B, LOW) ;
    digitalWrite (LED_C, LOW) ;
    digitalWrite (LED_D, HIGH) ;
    digitalWrite (LED_E, HIGH) ;
    digitalWrite (LED_F, LOW) ;
    digitalWrite (LED_G, LOW) ;
  } else if (num == 5) {
    digitalWrite (LED_A, LOW) ;
    digitalWrite (LED_B, HIGH) ;
    digitalWrite (LED_C, LOW) ;
    digitalWrite (LED_D, LOW) ;
    digitalWrite (LED_E, HIGH) ;
    digitalWrite (LED_F, LOW) ;
    digitalWrite (LED_G, LOW) ;
  } else if (num == 6) {
    digitalWrite (LED_A, LOW) ;
    digitalWrite (LED_B, HIGH) ;
    digitalWrite (LED_C, LOW) ;
    digitalWrite (LED_D, LOW) ;
    digitalWrite (LED_E, LOW) ;
    digitalWrite (LED_F, LOW) ;
    digitalWrite (LED_G, LOW) ;
  } else if (num == 7) {
    digitalWrite (LED_A, LOW) ;
    digitalWrite (LED_B, LOW) ;
    digitalWrite (LED_C, LOW) ;
    digitalWrite (LED_D, HIGH) ;
    digitalWrite (LED_E, HIGH) ;
    digitalWrite (LED_F, HIGH) ;
    digitalWrite (LED_G, HIGH) ;
  } else if (num == 8) {
    digitalWrite (LED_A, LOW) ;
    digitalWrite (LED_B, LOW) ;
    digitalWrite (LED_C, LOW) ;
    digitalWrite (LED_D, LOW) ;
    digitalWrite (LED_E, LOW) ;
    digitalWrite (LED_F, LOW) ;
    digitalWrite (LED_G, LOW) ;
  } else if (num == 9) {
    digitalWrite (LED_A, LOW) ;
    digitalWrite (LED_B, LOW) ;
    digitalWrite (LED_C, LOW) ;
    digitalWrite (LED_D, LOW) ;
    digitalWrite (LED_E, HIGH) ;
    digitalWrite (LED_F, LOW) ;
    digitalWrite (LED_G, LOW) ;
  }
  
  if (showDotPoint == 1) {
    digitalWrite (LED_DP, LOW) ;
  } else {
    digitalWrite (LED_DP, HIGH) ;
  }

  if (no == 1) {
    digitalWrite (DIGIT1, HIGH) ;
  } else if (no == 2) {
    digitalWrite (DIGIT2, HIGH) ;
  } else if (no == 3) {
    digitalWrite (DIGIT3, HIGH) ;
  } else if (no == 4) {
    digitalWrite (DIGIT4, HIGH) ;
  }
}
