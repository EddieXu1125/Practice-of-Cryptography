# -*- coding:UTF-8 -*-


def extract(secret_url,info_saved):
    from PIL import Image
    
    im = Image.open(secret_url)
    im = im.convert("RGB")
    width=im.size[0]
    height=im.size[1]
    length = 10000

#计数器
    count= 0
    wt=""

    for i in range(width):
        for j in range(height):
    # 获取像素点的值
            rgb = im.getpixel((i, j))
    # 提取R通道的附加值
            if count % 3 == 0:
                wt = wt + str(rgb[0] % 2)
                if count == length:
                    break
                count += 1
            #print(rgb[0]%2)
            if count == 16:
                length = int(wt[:16],2)
            #print("r",wt[:16])
            #print("提取长度",length)
                wt = ""
    # 提取G通道的附加值
            if count % 3 == 1:
                wt = wt + str(rgb[1] % 2)
            #print(rgb[1]%2)
                if count == length:
                    break
                count += 1
            if count == 16:
                length = int(wt[:16],2)
            #print("r",wt[:16])
            #print("提取长度",length)
                wt = ""

    # 提取B通道的附加值
            if count % 3 == 2:
                wt = wt + str(rgb[2] % 2)
                #print(rgb[2]%2)
                if count == length:
                    break
                count += 1
            if count == 16:
                length = int(wt[:16],2)
            #print("r",wt[:16])
            #print("提取长度",length)
                wt = ""
    print(count,' ',length,' ',len(wt))
    temp = 0
    content = ""
    #print(wt[20464:21861])
    for i in range(0,length-16,16):
        temp = chr(int(wt[i:i+16],2))
    #print(wt[i:i+15])
        content+=temp
    #print(content)
    with open(info_saved,"a",encoding = "utf-8") as f:
        f.write(content)
    f.close

# # 所嵌入的二进制比特流长度
# length = 2784

#含有隐藏信息的图片

secret_url = "D:\\Captures\\secret.png"

#信息提取出后所存放的文件

info_saved = "D:\\Captures\\get_flag.txt"

extract(secret_url,info_saved)
