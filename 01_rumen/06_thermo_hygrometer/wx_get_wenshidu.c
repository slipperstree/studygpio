#include <wiringPi.h>
#include <unistd.h>
#include <time.h>

// 接收到的40位数据
int bits[40];
// 5个数据分别储存湿度整数数据，湿度小数数据，温度整数数据，温度小数数据，校验和数据
int data[5];
// 定义温湿度计的data口连接的gpio口
#define DATA 7 //BCM: 4
// 定义一个阈值，用于判断当前数据位是0还是1。
#define VAL 200
// 如果取值失败则重新尝试取值的上限次数，10次就足够了
#define RETRY 10
#define TIME_START 20000
// 循环检测高低电平时，如果超过这个值就认为检测失败或者全部数据已经发送完成。
#define MAXCNT 10000

// 读取DHT11的温度湿度数据
void readDHT11();

int main (void) {
  wiringPiSetup () ;
  readDHT11();
  return 0 ;
}

void readDHT11() {
  int i,j,cnt = 0;

  for (j = 0; j < RETRY; ++j)
  {
    for (i = 0; i < 5; ++i) {
      data[i] = 0;
    }

    pinMode (DATA, OUTPUT) ;

    digitalWrite (DATA, HIGH);
    usleep(500000); 

    digitalWrite (DATA, LOW);
    usleep(TIME_START);
    digitalWrite (DATA, HIGH);
    pinMode (DATA, INPUT);

    cnt=0;
    while (digitalRead(DATA) == HIGH) {
      cnt++;
      if (cnt > MAXCNT)
      {
        //printf("DHT11未响应，请检查连线是否正确，元件是否正常工作。\n");
        exit(1);
      }
    }
    
    cnt=0;
    while (digitalRead(DATA) == LOW) {
      cnt++;
      if (cnt > MAXCNT)
      {
        //printf("DHT11未响应，请检查连线是否正确，元件是否正常工作。\n");
        exit(1);
      }
    }

    cnt=0;
    while (digitalRead(DATA) == HIGH) {
      cnt++;
      if (cnt > MAXCNT)
      {
        //printf("DHT11未响应，请检查连线是否正确，元件是否正常工作。\n");
        exit(1);
      }
    }

    // ##################### 40bit的数据传输开始 ######################
    for (i = 0; i < 40; i++)
    {
      while (digitalRead(DATA) == LOW) {
      }

      cnt=0;
      while (digitalRead(DATA) == HIGH) {
        cnt++;
        if (cnt > MAXCNT)
        {
          break;
        }
      }

      if (cnt > MAXCNT)
      {
        break;
      }

      bits[i] = cnt;
    }

    for (i = 0; i < 40; ++i) {
      data[i/8] <<= 1;
      if (bits[i] > VAL) 
      {
        data[i/8] |= 1;
      }
    }

    if (data[4] == (data[0] + data[1] + data[2] + data[3]) & 0xFF ) {
      printf("%d,%d\n", data[0], data[2] );
      break;
    } else {
      continue;
    }
  }
}
