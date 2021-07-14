def info_embed(image_url,saved_url):  
    #example  image_url = 'C:\\Users\\16492\\sak(8129277)\\無題(90168726).png' # 需要上传的图片的路径
    #         saved_url = 'C:\\Users\\16492\\goatwillow(13788343)' # 含密图像的保存路径
    #         info_url = ''
    from PIL import Image
    import os,sys
    import collections
    # def encode2b(s):
    #     return ' '.join([bin(ord(c)).replace('0b', '') for c in s])

    # def decode2d(s):
    #     return ''.join([chr(i) for i in [int(b, 2) for b in s.split(' ')]])
    def encode(s):
        c = ""
        temp = ""
        for i in s:
            temp = bin(ord(i)).replace('0b','')
            temp = temp.zfill(16)
            c += temp
        length = len(c)
        #print(length)
        if length>65535:
            print("嵌入信息过长！")
            return False
        temp = bin(length+16).replace('0b','')
        temp = temp.zfill(16)#填充16位定长数据长度header
        c = temp + c
        return c

    def getAllDirQueue(path): # 提取秘密信息（遍历上传图片所在文件夹内的所有文件夹和文件）
        info = ''
        queue = collections.deque()
        queue.append(path)
        while len(queue) != 0:
            dirpath = queue.popleft()
            filelist = os.listdir(dirpath)
            for listname in filelist:
                fileabspath = os.path.join(dirpath, listname) 
                if os.path.isdir(fileabspath):
                    info = info + ("目录文件夹名："+listname)
                    queue.append(fileabspath)
                else:
                    info = info + ("文件"+fileabspath) 
        return info


    # 主函数
    dir_abspath = os.path.abspath(os.path.dirname(image_url))
    
    s = getAllDirQueue(dir_abspath)
    #print(s)
    filelist_2 = encode(s)
    
    length = len(filelist_2) # 需要传参的值
    print(length)

    img = Image.open(image_url)
    img = img.convert("RGB")
#print(filelist)
#print(len(filelist)%16)
#lsb
    
    count = 0
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            data = img.getpixel((x, y))
            r = data[0]
            g = data[1]
            b = data[2]
            # 计数器
    # 二进制像素值的长度，可以认为要写入图像的文本长度，提取（解密）时也需要此变量
            if count == length:
	            break
            r = (r - r % 2) + int(filelist_2[count])
        #print(int(filelist[count]),' ',r%2)
            count += 1
            if count == length:
	            img.putpixel((x, y), (r, g, b))
	            break

            g = (g - g % 2) + int(filelist_2[count])
        #print(int(filelist[count]),' ',g%2)
            count += 1
            if count == length:
	            img.putpixel((x, y), (r, g, b))
	            break

            b = (b - b % 2) + int(filelist_2[count])
            #print(int(filelist[count]),' ',b%2)
            count += 1
            if count == length:
	            img.putpixel((x, y), (r, g, b))
	            break
# 每3次循环表示一组RGB值被替换完毕，可以进行写入
            if count % 3 == 0:
	            img.putpixel((x, y), (r, g, b))
    img.save(saved_url)
    





    


info_embed('D:\\Captures\\1.png','D:\\Captures\\secret.png')