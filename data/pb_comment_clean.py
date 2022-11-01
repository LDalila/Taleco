import json
from tqdm import tqdm

banned = ['friv100play', 'pharmacyschooling', 'weightlosspunch', 'healthylivingmagazine', 'beats studio', 'vuittonhandbags', 'belanja-online', 'friend need information on topic', 'thanks for website', 'nike brand sports', 'designer handbags', 'kostümler', 'sapphire crystal', 'replica watches', 'inspirar el sentiment', 'pens for sale', 'michael kors', 'shopping airlines', 'free shipping', 'online earn money', ' nike ', '.biz', 'tattoo removal', 'chinasite', 'jerseyshop', 'insurancesecret', 'nba jerseys', 'paydayloan', 'learning edge of some sort', 'air-jordan', 'requintn', 'page optimization', 'luxury brand', 'jeremy scott wings', 'air jordan', 'wipe there ass', 'tnrias', 'cowboysjersey', 'digitalaccessory', 'jimmy-choo', 'themepack', 'hieghr', 'nomarl', 'cash advances for bad credit', 'descuendos', 'sexy pole', 'cheapjersey', 'nice readiness', 'digital accessor', 'delesandro', 'oakley', 'wholesale jerseys', 'debtquotes', 'taojiumei', 'roller bearing', 'jrlaw.org', 'monsterbeatsstudio', 'scots-titles', 'ina bearing', 'betäuben', 'it company india', '  steroids  ', 'slimming coffee', ' my blog ', 'dinodirect', 'pay day loan', 'towing and recovery', 'monster beats', 'quilter', 'badcreditloans', '7fiz', 'mastiya', 'phlebotomytraining', 'sampleresume', 'forexpros', ' holiday ', 'empathicexit', 'gotoget', 'widze', 'monsterbuy', 'finseth', 'air max', 'gfaonline', 'indviklet', 'sunglass', 'xiaoxiao', ' ugg ', 'ankaraotokiarlamasirketleri', 'nikemall', 'tramadol']
banned_users = ['pas cher', 'boutique', 'fdgfdhg', 'replica watches', 'makeup', 'chaussures', 'for sale', 'chili01234', 'michael kors', 'clothing', 'wholesale', ' free ', 'louboutin', 'outlet', ' sko', 'out source', 'handbag', 'sac ', 'sonic games', 'discount', 'watches', 'cheap', 'medical', 'desarrollo', 'alcalina', 'credit score', 'worst recovery', 'running shoes', ' shoes', 'share market', 'giuhoih', 'sdhadfkji', 'seattle lawyer', 'foreclosure', 'defense attorney', 'attorney riverside', 'gucci', 'tee shirt', 'scarpe online', 'fake', ' jersey', 'seobeauty', 'adidas', 'acrylic', 'kkong', 'cash tip', 'tatueringar', 'WuMengjie', 'localisateur', 'kamagra', 'descuento', 'online ', 'e-learning', 'certificados', 'facebook', 'attorney orange', 'new ghd', 'red wine glasses', 'racing hats', 'bottle opener', 'vuitton', 'Kavin Matthews', 'frogskins' , 'casquette', 'prix', 'mortgage', 'air jordan', 'app developer', 'chinaamanda', 'wine barrel', 'edge cutting', 'jordan take', 'metal bed', 'equipment', 'keylogger', 'brandshops', 'monster ladygaga', 'adult high', 'alfred smith', 'tom henry', ' mbt', 'i need a better blog', 'dental', ' sox ', 'mbt ', 'chaussure', 'new era', 'nike ', 'sherwani', 'coach bag', 'tn requin', 'maillot', 'coach poppy', 'film izle', ' bearings', 'viagra', 'block machine', ' sale', 'ray ban', 'smith online', 'lawyers surrey', 'commodities', ' mobil ', 'freight brokers', ' online', 'job vacancies', 'monster beats', 'business market', 'dtc ', 'jdj tajdas', 'anna e. dant', 'mobile phones review', 'bine', ' hats', 'high school diploma', 'sunglasses', 'advertising', 'solenoid', 'magasin', 'high quality', ' spy', 'duct cleaning', 'cialis', ' premium ', ' hire', 'apparel', 'beats monster', 'kriti gupta', 'air max', ' mobil', 'free run', 'steroid', 'burberry ', 'estate planning', 'fadli', 'spy ', 'fuelcentral', 'aditi', 'kamrun nahar', 'web ', 'sonderpostenhandel', 'kobe 7', 'wedding dress', 'vijayasingh', 'herbalife', 'rental', 'şampuan', 'stocktips', 'sex site', 'educational toys', 'golden lovita', 'jordan 4', 'lokopertiop', 'thermometer', 'services', 'criminal law', 'fatemeh ghanbari', 'iphone', 'insurance', 'delivery', 'dial a bottle', 'liquor', 'calgary', 'Kamran Habib Khan', 'mlb cap', 'lawyers', 'bankruptcy', ' service', 'cincinnati', 'lisawhite', 'somya', 'dailylinkbuilding', 'coffeemaker', 'scholarship', 'hoodie', 'voyeur', 'management software', 'jordan retro', 'copie borse', 'top ', 'beats ', 'free standing', 'persianas', 'sözleri', ' coats', 'xiaoying', 'solicitors', 'plumber', 'fxopen', 'property inventories', 'ankara', 'stubman', 'paul smith' 'amailiu', 'Paul Smith', 'escort', 'attorney', 'jenny tabassum', 'bearing', 'freelance', 'writer jobs', 'cricket', 'Miles34Latasha', 'ferf', 'office 2010', 'femmes', 'onitsuka', 'healing method', 'religion store', 'cartoner', 'rc helicopter', ' ugg ', 'custom essay', 'baseball caps', 'north face', 'Moncler', 'sell my gold', 'APA Citation Machine', 'quilted', 'headphones', 'ugg boots', 'marty weil', 'chi flat irons', 'gfdgdfgd', 'wedding', ' nike', 'ugg ', 'air force one', 'uggs ']
banned_exact_users = ['lee']

stop_times = {
    143: '07/10/2012 at 06:18 PM',
    144: '07/19/2012 at 02:14 AM',
    147: '07/16/2012 at 01:24 AM',
    149: '06/13/2012 at 04:38 PM',
    150: '06/16/2012 at 11:11 PM',
    152: '06/08/2012 at 04:23 PM',
    154: '06/28/2012 at 04:10 PM',
    155: '07/12/2012 at 01:34 PM',
    156: '06/06/2012 at 08:03 AM',
    157: '06/09/2012 at 11:35 AM',
    158: '06/06/2012 at 04:25 AM',
    159: '06/07/2012 at 04:00 PM',
    161: '05/24/2012 at 12:52 AM',
    162: '05/18/2012 at 01:39 AM',
    163: '05/09/2012 at 09:39 AM',
    164: '04/30/2012 at 05:46 AM',
    165: '05/06/2012 at 08:38 AM',
    166: '04/23/2012 at 05:56 PM',
    167: '04/20/2012 at 05:13 PM',
    168: '04/26/2012 at 09:31 PM',
    169: '04/27/2012 at 10:27 AM',
    170: '04/26/2012 at 09:41 PM',
    171: '05/01/2012 at 03:31 PM',
    172: '04/16/2012 at 04:53 AM',
    173: '04/12/2012 at 10:25 AM',
    174: '04/13/2012 at 03:01 PM',
    176: '04/08/2012 at 11:14 PM',
    177: '03/19/2012 at 07:55 AM',
    178: '04/15/2012 at 07:54 PM',
    179: '04/08/2012 at 06:51 PM',
    180: '03/04/2012 at 03:53 PM',
    181: '02/23/2012 at 12:45 PM',
    182: '02/20/2012 at 11:34 AM',
    183: '02/14/2012 at 01:39 AM',
    184: '02/20/2012 at 06:01 AM',
    185: '02/08/2012 at 08:40 PM',
    186: '02/14/2012 at 06:17 AM',
    187: '02/05/2012 at 06:53 AM',
    188: '12/11/2011 at 04:47 PM',
    189: '12/07/2011 at 10:23 PM',
    190: '12/20/2011 at 08:31 AM',
    191: '12/03/2011 at 08:13 PM',
    192: '12/03/2011 at 02:23 AM',
    193: '12/23/2011 at 05:43 AM',
    194: '11/27/2011 at 10:30 PM',
    195: '11/28/2011 at 01:23 PM',
    196: '01/13/2012 at 06:06 AM',
    197: '11/15/2011 at 11:52 PM',
    198: '02/20/2012 at 06:37 AM',
    199: '11/03/2011 at 09:06 PM',
    200: '11/01/2011 at 07:05 PM'
}

keep = {
    154: [-1],
    155: [-3],
    158: [-12],
    163: [-1],
    167: [-1, -2],
    169: [-3],
    171: [-3],
    180: [-1, -16, -32],
    181: [-61],
    182: [-12, -17],
    183: [-48],
    184: [-34],
    185: [-64],
    186: [-11, -13, -43, -48],
    187: [-84],
    188: [-41, -42, -49, -53, -55],
    189: [-28, -46, -47, -50, -51, -55, -58, -59, -60, -61, -62, -63, -64, -66, -67, -68, -69, -70, -71, -72, -73, -80, -81, -82, -83],
    190: [-50],
}

with open('becker-posner.json') as f:
	data = json.load(f)

stop_at = 200

total_counter = 0
for i, post in enumerate(tqdm(data)):
    if i < stop_at:
        continue
    #print(post['text'])
    stop = False
    counter = 0
    for j, comment in enumerate(post['comments']):
        if not stop or stop and i in keep and j - len(post['comments']) in keep[i]:
            cdt = comment['author'].lower() not in banned_exact_users and all(x.lower() not in comment['text'].lower() for x in banned) and all(x.lower() not in comment['author'].lower() for x in banned_users)
            if cdt:
                counter += 1
                if i > stop_at:
                    print(f'----------- {counter} / {j + 1} / {len(post["comments"])} -----------')
                    print(comment['text'])
                    print(comment['author'], comment['date'])
                    print()
            if i in stop_times.keys() and stop_times[i] in comment['date']:
                stop = True
    if i > stop_at:
        if post['comments']:
            input()
            for j in range(20):
                print()
    print(counter)
    total_counter += counter
    if i == stop_at:
        total_counter_sub = total_counter
print('===')
print(total_counter, sum(len(x['comments']) for x in data))
print(total_counter_sub, sum(len(x['comments']) for x in data[:stop_at]))