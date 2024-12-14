# DETEECT
## DETEECT Senior Year Project Repo
### Defection_trial1 dosyası image subtraction yapıyor ve fark bulunan yerlere red circle atıyor orig - defect ve pcb2orig pcb2defected fotoğraflarını kodda deneyip görebilirsiniz. (pcb2 için threshold değerini 0-10 arası küçük bir değer yapın diğeri için 130 iyi)
### Auto_white_balance dosyası çekilen resimlerin renk dengelemesi için en küçük ve en büyük renk değerlerini tespit edip bunları gerçek beyaz ve siyaha eşitliyor aradaki diğer renkleri de ona göre scale ediyor. yüklediğim resimden farkı görebilirsiniz. Işığa karşı olan hassasiyetimizi azaltıyor 
### image_cropping dosyası çekilen resimlerden pcbyi cropluyor
### mask_creation dosyası bize verilen assembly filelardaki dikdörtgen şekilleri tespit edip o koordinatlara beyaz dikdörtgenler çizip arka planı siyah bırakıyor. Assembly içerisinde bütün komponentler kapalı dikdörtgen olarak verilmediği için kod geliştirilmeye açık.
