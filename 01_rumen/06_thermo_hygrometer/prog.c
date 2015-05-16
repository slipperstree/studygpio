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
unsigned char wendu = 0;
// 湿度数据变量
unsigned char shidu = 0;
// 为了每分钟自动重取一次数据，记住上一次取数据时的分钟数
unsigned char lastMin = 60;

// 定义温湿度计的data口连接的gpio口
#define DATA 7 //BCM: 4

// 根据DHT11的硬件时序图定义各种延时所需的时间间隔(单位：微秒)
// 总线空闲状态为高电平,主机把总线拉低等待DHT11响应,
// 主机把总线拉低必须大于18毫秒,保证DHT11能检测到起始信号。
#define TIME_START 20000

// 主机发送开始信号结束后,延时等待20-40us后, 读取DHT11的响应信号,
// 主机发送开始信号后,可以切换到输入模式,或者输出高电平均可, 总线由上拉电阻拉高。
#define t_pi_start_wait 1000

// DHT11接收到主机的开始信号后,等待主机开始信号结束,然后发送80us低电平响应信号。
// 总线为低电平,说明DHT11发送响应信号,DHT11发送响应信号后,再把总线拉高80us,
#define t_dht11_start_resp 80

// 准备发送数据,每一bit数据都以50us低电平时隙开始,高电平的长短定了数据位是0还是1。
#define t_dht11_data_head 50
#define t_dht11_data_0 26
#define t_dht11_data_1 70

#define MAXCNT 1000

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

  digitalWrite (DIGIT1, HIGH) ;
  digitalWrite (DIGIT2, HIGH) ;
  digitalWrite (DIGIT3, HIGH) ;
  digitalWrite (DIGIT4, HIGH) ;

  for (; ; )
  {
    time(&now);
    tm_now=localtime(&now);

    if (tm_now->tm_min != lastMin)
    {
      readDHT11();
    }

    // 默认显示温度，按钮按下时显示湿度
    if (digitalRead(btn) == HIGH) {
      usleep(t);
      showDigit(1, 0, FALSE);
      usleep(t);
      showDigit(2, 0, FALSE);
      usleep(t);
      showDigit(3, wendu / 10, FALSE);
      usleep(t);
      showDigit(4, wendu % 10, FALSE);
    } else {
      usleep(t);
      showDigit(1, 0, FALSE);
      usleep(t);
      showDigit(2, 0, TRUE);
      usleep(t);
      showDigit(3, shidu / 10, FALSE);
      usleep(t);
      showDigit(4, shidu % 10, FALSE);
    }
  }
  return 0 ;
}

int bits[100], data[5];
void readDHT11() {
  int i = 0;
  unsigned char bit = 0;
  int waitTime = 0;
  int cnt=0;

  // 将温度湿度清零
  shidu = 0;
  wendu = 0;

  // GPIO口模式设置为输出模式
  pinMode (DATA, OUTPUT) ;

  digitalWrite (DATA, HIGH);
  usleep(500000);  // 500 ms

  // 拉低DATA口，输出开始指令（至少持续18ms）
  digitalWrite (DATA, LOW);
  usleep(TIME_START);
  digitalWrite (DATA, HIGH);
  
  // 开始指令输出完毕，切换到输入模式，等待DHT11输出信号。
  // 由于有上拉电阻的存在，所以DATA口会维持高电平。
  pinMode (DATA, INPUT);

  // 在DATA口被拉回至高电平通知DHT11主机已经准备好接受数据以后，
  // DHT11还会继续等待20-40us左右以后才会开始发送反馈信号，所以我们把这段时间跳过去
  // 如果长时间（1000us以上）没有低电平的反馈表示有问题，结束程序
//printf("等待DHT11发送反馈信号。\n");
  cnt=0;
  while (digitalRead(DATA) == HIGH) {
    cnt++;
    if (cnt > MAXCNT)
    {
      printf("DHT11未响应，请检查连线是否正确，元件是否正常工作。\n");
      exit(1);
    }
  }
  
//printf("DHT11发送了反馈信号。\n");
  // 这个反馈响应信号的低电平会持续80us左右，但我们不需要精确计算这个时间
  // 只要一直循环检查DATA口的电平有没有恢复成高电平即可
  cnt=0;
  while (digitalRead(DATA) == LOW) {
    cnt++;
    if (cnt > MAXCNT)
    {
      printf("DHT11未响应，请检查连线是否正确，元件是否正常工作。\n");
      exit(1);
    }
  }

//printf("DHT11发送了反馈信号以后拉高信号。\n");
  // 这个持续了80us左右的低电平的反馈信号结束以后，DHT11又会将DATA口拉回高电平并再次持续80us左右
  // 然后才会开始发送真正的数据。所以跟上面一样，我们再做一个循环来检测这一段高电平的结束。
  cnt=0;
  while (digitalRead(DATA) == HIGH) {
    cnt++;
    if (cnt > MAXCNT)
    {
      printf("DHT11未响应，请检查连线是否正确，元件是否正常工作。\n");
      exit(1);
    }
  }
  
// printf("40bit的数据传输开始###########################################\n");

  // ######### 40bit的数据传输开始 ##########
  for (i = 0; i < 100; i++)
  {
    // 每一个bit的数据（0或者1）总是由一段持续50us的低电平信号开始
    // 跟上面一样我们用循环检测的方式跳过这一段
    cnt = 0;
    while (digitalRead(DATA) == LOW) {
      cnt++;
      if (cnt > MAXCNT)
      {
       printf("DHT11未响应，请检查连线是否正确，元件是否正常工作。\n");
       exit(1);
      }
    }
//printf("持续%d的低电平信号结束。\n", cnt);
    // 接下来的高电平持续的时间是判断该bit是0还是1的关键。
    //    根据DHT11的说明文档，我们知道 这段高电平持续26us-28us左右的话表示这是数据0。
    //    如果这段高电平持续时间为70us左右表示这是数据1。
    // 方法1：在高电平开始的时候记下时间，在高电平结束的时候再记一个时间，
    //        通过计算两个时间的间隔就能得知是数据0还是数据1了。
    // 方法2：在高电平开始的以后我们延时40us，然后再次检测DATA口:
    //        (a) 如果此时DATA口是低电平，表示当前位的数据已经发送完并进入下一位数据的传输准备阶段（低电平50us）了。
    //        由于数据1的高电平持续时间是70us，所以如果是数据1，此时DATA口应该还是高电平才对，
    //        据此我们可以断言刚才传输的这一位数据是0。
    //        (b) 如果延时40us以后DATA口仍然是高电平，那么我们可以断言这一位数据一定是1了，因为数据0只会持续26us。
    // 方法3：循环检测电平状态并计数，每检查一次如果电平状态没变就让计数器加一，一直到电平状态变成低电平为止。
    //        数据0的高电平持续时间短，所以计数一定比数据1的计数少，由于微秒级别的延时太短，这个计数会有一定误差。
    //        我们需要先在自己的树莓派上用printf打印出每一位数据计数的结果，然后观察计数结果来设定一个阈值，
    //        高于这个阈值的就认为的数据1，低于这个值的就认为是数据0。
    // 我们这里采用简单易行的方法3。
    // 实际上，由于要求的时序太短，在树莓派上很难通过方法1和方法2实现。
    //    特别是方法2，因为linux里有一个系统级的延时函数usleep，单位确实是微秒。
    //    貌似用usleep(40)就可以了，实际测试的结果是延时远远超过40us。其原因是usleep这个函数的延时方法是
    //    暂停当前进程并放开cpu权限让cpu可以在这段时间里去处理其他任务。这样做的好处是不会浪费cpu资源，
    //    但问题是当系统将cpu权限交还给我们的进程的这个过程本身就要耗费若干ms（毫秒哦）
    //    所以导致usleep这个函数实际上没有办法做到延时几十微秒。
    cnt=0;
    while (digitalRead(DATA) == HIGH) {
      cnt++;
      if (cnt > MAXCNT)
      {
        printf("DHT11未响应，请检查连线是否正确，元件是否正常工作。\n");
        exit(1);
      }
    }

    bits[i] = cnt;
    printf("bits[%d] = %d (%d) \n", i, cnt, cnt>200?1:0 );
//printf("持续%d的高电平信号结束。第%d位。\n", cnt, i);


/*
    if (cnt < 200) {
      bit = 0;
//printf("数据0。\n");
    } else {
      bit = 1;
//printf("数据1。\n");
    }

    // 湿度的整数数据（40位信号的前8位）
    if (i < 8)
    {
      bit <<= i;
      shidu |= bit;

      if (i==7)
      {
        printf("shidu=%d \n", shidu);
      }
    }
    // 湿度的小数数据（40位信号的9-16位）
    // 根据官方文档说明可知，这款DHT11输出的小数位始终为0，所以我们不使用该数据，丢弃
    else if (i < 16)
    {
    }
    // 温度的整数数据（40位信号的17-24位）
    else if (i < 24)
    {
      bit <<= (i/8);
      wendu |= bit;

      if (i==23)
      {
        printf("wendu=%d \n", wendu);
        //exit(0);
      }
    }
    // 温度的小数数据（40位信号的25-32位）
    // 同湿度小数位，丢弃
    else if (i < 32)
    {
    }
    // 8位校验数据（40位信号的33-40位）
    // 可用于检测数据是否接收正确，本文不使用丢弃
    else 
    {
    }
*/
  }
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
