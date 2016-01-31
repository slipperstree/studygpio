#include <wiringPi.h>
#include <unistd.h>
#include <time.h>

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

#define VPRG 0    //BCM：17
#define SIN  23   //BCM：13
#define SCLK 24   //BCM：19
#define XLAT 2    //BCM：27
#define BLANK 4   //BCM：23
#define DCPRG 1   //BCM：18
#define GSCLK 7   //BCM：4

#define FALSE 0
#define TRUE  1

int i,n=0;

void resetBLACK();

int main (void) {
  wiringPiSetup () ;

  pinMode (VPRG, OUTPUT) ;
  pinMode (SIN, OUTPUT) ;
  pinMode (SCLK, OUTPUT) ;
  pinMode (XLAT, OUTPUT) ;
  pinMode (BLANK, OUTPUT) ;
  pinMode (DCPRG, OUTPUT) ;

  // 注意，这里我们设置输出模式为时钟模式
  // 在这个模式下，GPIO4引脚可以稳定高速的输出时钟信号（方波），并且不会额外占用CPU资源
  // 可以使用这个模式的引脚只有GPIO4，这个引脚是树莓派硬件支持时钟信号输出的
  pinMode (GSCLK, GPIO_CLOCK) ;

  // 设置时钟频率，最高19.2MHz，或者是19.2Mhz的n分频，这里我们设置GSCLK为2.4MHz（19.2Mhz/8）
  // 设置BLANK为585Hz （2.4Mhz/4096）
  gpioClockSet (GSCLK, 9600000) ;

  // VPRG设置为L，使其工作在GS mode
  digitalWrite (VPRG, LOW) ;

  // BLANK设置为H，关闭所有输出
  digitalWrite (BLANK, HIGH) ;

  digitalWrite (DCPRG, HIGH) ;

  // 传送12bit X 16组PWM数值GSn(n=0-15)，共192bit
  // 每组数据的值范围是0-4095
  // 因为是通过移位寄存器传输，所以传送顺序是倒序的：GS15，GS14。。。GS0
  // GSn决定了OUTn的PWM调宽。（GSn / 4095 = 0% - 100%）
  for (i = 0; i < 192-36; ++i)
  {
    digitalWrite (SIN, LOW) ;
    // 创造SCLK的上升沿，写SIN数据到移位寄存器中
    digitalWrite (SCLK, LOW) ;
    digitalWrite (SCLK, HIGH) ;
  }

  // OUT2
  n=11;
  for (i = 0; i < 12-n; ++i)
  {
    digitalWrite (SIN, LOW) ;
    // 创造SCLK的上升沿，写SIN数据到移位寄存器中
    digitalWrite (SCLK, LOW) ;
    digitalWrite (SCLK, HIGH) ;
  }
  for (i = 0; i < 12; ++i)
  {
    digitalWrite (SIN, HIGH) ;
    // 创造SCLK的上升沿，写SIN数据到移位寄存器中
    digitalWrite (SCLK, LOW) ;
    digitalWrite (SCLK, HIGH) ;
  }

  // OUT1
  n=9;
  for (i = 0; i < 12-n; ++i)
  {
    digitalWrite (SIN, LOW) ;
    // 创造SCLK的上升沿，写SIN数据到移位寄存器中
    digitalWrite (SCLK, LOW) ;
    digitalWrite (SCLK, HIGH) ;
  }
  for (i = 0; i < n; ++i)
  {
    digitalWrite (SIN, HIGH) ;
    // 创造SCLK的上升沿，写SIN数据到移位寄存器中
    digitalWrite (SCLK, LOW) ;
    digitalWrite (SCLK, HIGH) ;
  }

  // OUT0
  n=5;
  for (i = 0; i < 12-n; ++i)
  {
    digitalWrite (SIN, LOW) ;
    // 创造SCLK的上升沿，写SIN数据到移位寄存器中
    digitalWrite (SCLK, LOW) ;
    digitalWrite (SCLK, HIGH) ;
  }
  for (i = 0; i < n; ++i)
  {
    digitalWrite (SIN, HIGH) ;
    // 创造SCLK的上升沿，写SIN数据到移位寄存器中
    digitalWrite (SCLK, LOW) ;
    digitalWrite (SCLK, HIGH) ;
  }

  // 送完GS数据后，创造XLAT的上升沿，将移位寄存器的数据一次性送入GS寄存器
  digitalWrite (XLAT, LOW) ;
  digitalWrite (XLAT, HIGH) ;

  // BLANK设置为L，打开所有输出
  digitalWrite (BLANK, LOW) ;

  // 准备工作完毕，下面向GSCLK输送时钟信号（高低电平交互的方波信号）
  // TLC5940会根据这个时钟信号进行从0-4095的计数，一边计数一边检查各GSn的设定值，一旦到达GSn的值，则切换OUTn的电平
  // 一直计数到4095为止，再从0开始重新计数。从0计数到4095就是一个高低电平的切换周期。
  // 所以我们给5940提供的时钟频率越快，最后输出的PWM频率就越快
  // 最后输出的PWM的频率 = 时钟信号的频率 / 4095
  // 比如时钟频率是8M，则最后从各OUT口输出的PWM频率是8MHz / 4095 = 1.953KHz
  // 根据TLC5940的官方文档，GSCLK可支持最高30MHz的时钟频率，也就是最高可以输出7.3KHz的PWM信号。
  // 如果是控制LED的亮度，那么让人眼感觉不到闪烁的最低频率应该是50Hz以上，
  // 所以我们应该至少给GSCLK提供不低于50 X 4095 = 200KHz的方波。
  // 树莓派Python的GPIO库翻转IO口的速度不高，实测速度只能达到60KHz，
  // 导致最后输出的PWM频率只有14Hz，会有明显的闪烁感
  // 后来查了相关资料，发现树莓派GPIO4是硬件支持时钟信号输出的，速度可达到19.2Mhz，于是本文采用此方法
  resetBLACK();

  return 0 ;
}

void resetBLACK() {
  n=0;
  while(1){
    n+=1;
    if (n>=4000) {
      digitalWrite (BLANK, HIGH) ;
      digitalWrite (BLANK, LOW) ;
      n=0;
    }
  }
}