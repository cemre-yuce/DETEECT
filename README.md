# DETEECT
## DETEECT Senior Year Project Repo

5- Template_matching dosyası daha önceden oluşturulmuş bir klasör içine seçilen koordinatlardaki resmi kaydediyor. Önce golden unit resminizi image_path kısmına, template klasörünüzü my_path kısmına girin. Runladıktan sonra bütün komponentleri tek tek dikdörtgen içine seçin, seçilen kısımlar siyaha dönecek. Daha sonra my_path kısmı aynı kalacak şekilde sadece image_path kısmına test etmek istediğiniz pcbyi girin (internetteki AI toollarıyla object silmek mümkün mesela bir resistoru resimden silin). Test etmek istediğniz cpb ve golden unit pcb image aynı sizeda olmalı. Tekrar kodu runladığınızda hata tespit edilmeyen komponentlerin üzeri siyah kalacak diğerleri ise ekranda görünecektir klavyede "d" tuşuna basarak tespit edilen defectlerin etrafına dikdörtgen de çizdirebilirsiniz. Yeni bir pcb golden unit oluşturacağınızda my_path kısmına yeni bir klasör girmelisiniz böylece farklı pcblerin templateleri karışmamalı.

4-mask_creation dosyası bize verilen assembly filelardaki dikdörtgen şekilleri tespit edip o koordinatlara beyaz dikdörtgenler çizip arka planı siyah bırakıyor. Assembly içerisinde bütün komponentler kapalı dikdörtgen olarak verilmediği için kod geliştirilmeye açık.

3-image_cropping dosyası çekilen resimlerden pcbyi cropluyor

2-Auto_white_balance dosyası çekilen resimlerin renk dengelemesi için en küçük ve en büyük renk değerlerini tespit edip bunları gerçek beyaz ve siyaha eşitliyor aradaki diğer renkleri de ona göre scale ediyor. yüklediğim resimden farkı görebilirsiniz. Işığa karşı olan hassasiyetimizi azaltıyor 

1-Defection_trial1 dosyası image subtraction yapıyor ve fark bulunan yerlere red circle atıyor orig - defect ve pcb2orig pcb2defected fotoğraflarını kodda deneyip görebilirsiniz. (pcb2 için threshold değerini 0-10 arası küçük bir değer yapın diğeri için 130 iyi)

