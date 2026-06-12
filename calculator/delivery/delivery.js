/* ============================================================
   delivery.js — универсальный модуль «Доставка».

   Использование:
     <link rel="stylesheet" href="delivery.css">
     <div id="dlv"></div>
     <script src="delivery.js"></script>
     <!-- zones-data.js опционален — координаты зон уже встроены в delivery.js -->
     <script>Kosmos.mountDelivery(document.getElementById('dlv'));</script>

   Опции mountDelivery(host, { yandexApiKey: '...' }) — ключ API Яндекс.Карт.

   Получает данные о торте через ЛЮБОЙ из 3-х каналов одновременно:
     1) URL params         (?total=..&cake=..&weight=..&tiers=..&filling=..&tiered=0|1)
     2) BroadcastChannel   'kosmos-cake' — для блоков на одной странице
     3) window 'message'   — postMessage из родителя
     4) window 'kosmos-cake' CustomEvent — если калькулятор и доставка на одной странице
   ============================================================ */

(function(global){
  var TELEGRAM_URL = 'https://t.me/kosmoscake';

  var SPARKLE_SVG = '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">' +
    '<path d="M50 4 C52 38, 62 48, 96 50 C62 52, 52 62, 50 96 C48 62, 38 52, 4 50 C38 48, 48 38, 50 4 Z"/>' +
    '</svg>';

  var MAP_CENTER = [55.747674, 37.637463];
  var MAP_ZOOM = 9;

  /* Ключ с https://developer.tech.yandex.ru/ — для геокодера Яндекса (опционально).
     Карта и поиск адреса работают и без ключа (Nominatim). */
  var DEFAULT_YANDEX_API_KEY = '';

  function normalizeApiKey(key){
    key = (key || '').trim();
    if (!key) return '';
    if (/your[-_]?api[-_]?key/i.test(key) || key === '...' || key.length < 8) return '';
    return key;
  }

  var EMBEDDED_DELIVERY_ZONES = [{"key":"orange","rate":1000,"polygons":[{"coordinates":[[[55.646357966502826,37.390116656364825],[55.65526369703825,37.38754173571053],[55.70855845280961,37.33981987291752],[55.74827592546777,37.320937121452694],[55.79801077287082,37.32402702623781],[55.828941921170944,37.34771629625734],[55.85926911820345,37.35183616930421],[55.894395757531136,37.38754173571045],[55.91387534519685,37.46032615953858],[55.93122511682321,37.529334033073745],[55.933923269268234,37.61207481676515],[55.927160700643185,37.716260353244834],[55.89360723811185,37.81376401535423],[55.849403346159725,37.89753476730729],[55.81365586893191,37.93152371994402],[55.80060465328661,37.935643592990886],[55.79291688146982,37.9363302384987],[55.78810520489952,37.93667356125262],[55.77950798542229,37.936845222629564],[55.76800577245939,37.93667356125262],[55.76316680951978,37.93701688400654],[55.74980814203732,37.937703529514295],[55.72995526066772,37.93787519089122],[55.71769951939411,37.937617698825775],[55.70854152379436,37.937703529514295],[55.6815880393859,37.93701688400643],[55.66791025269682,37.934956947483],[55.65636285145335,37.92706052414316],[55.61830014995897,37.88723508469007],[55.595525782845115,37.813535210536074],[55.61372320194039,37.77575415414293],[55.62193214702953,37.79094618600328],[55.624397065575586,37.79553375784375],[55.62760225466585,37.800597768463874],[55.632069654795124,37.807292562165046],[55.646057589052546,37.82836141477216],[55.65023167733959,37.83471288571943],[55.65125086358424,37.836214922767766],[55.65210016510386,37.836987398964055],[55.657438208175904,37.839519404274114],[55.65917830146489,37.84001622454408],[55.660270035130324,37.84005913988832],[55.66313265818558,37.839801647822895],[55.66970619149703,37.83757004992249],[55.68362440667723,37.83236871461093],[55.69041700141414,37.82987744458252],[55.69368948530003,37.82953412182863],[55.696040655738834,37.829705783205576],[55.698779469025496,37.83039242871339],[55.710061727648835,37.83612519566107],[55.71625591308181,37.83923735717924],[55.72960510490273,37.84043808743407],[55.74366455765235,37.84199432372338],[55.75736413853379,37.843195953362056],[55.76180514930543,37.84331688913772],[55.774990368254755,37.84331688913772],[55.77893826770027,37.84312545575619],[55.78423474817734,37.842395894904136],[55.79588698421516,37.841040557528565],[55.80844378231004,37.839617846692384],[55.82188444013351,37.83777867927305],[55.82824404457624,37.83182694761078],[55.8366251835832,37.81547620145599],[55.84485963680213,37.79951169339933],[55.89357848595344,37.704110883157504],[55.894928901810296,37.69140794126296],[55.89637572358093,37.655702374856716],[55.897991277187536,37.63948037473464],[55.90001665194337,37.62737824765945],[55.901849042365164,37.61939599363114],[55.91084096152505,37.58343293515942],[55.91121457505812,37.578798077981716],[55.91114226304353,37.57579400388505],[55.91039503095649,37.56489350644851],[55.9077434455856,37.5413329824617],[55.90641758461852,37.53120496122147],[55.9053809707069,37.52665593473221],[55.903476421468035,37.52124860135819],[55.90251205692398,37.51905991880202],[55.89151659919263,37.49507024137284],[55.887127187419814,37.48288228360915],[55.88338855899454,37.46644570676589],[55.882351327024544,37.447305463235615],[55.882037739782355,37.44558884946605],[55.87827449451801,37.43335797635813],[55.87096406743187,37.4110419973542],[55.87048148235641,37.410355351846384],[55.86985411276329,37.409454129617394],[55.86394186099789,37.40108563749092],[55.85899418031209,37.397352002542156],[55.85231331486033,37.393758092822445],[55.847853056304,37.39176252931535],[55.84453317973661,37.392170225085636],[55.842842951377925,37.39320019334734],[55.83871365459466,37.39545324891983],[55.83676959340277,37.39583948701796],[55.83272418425905,37.39541033357556],[55.8229651598707,37.392749582232796],[55.808853708745,37.38828638643203],[55.80285962012242,37.38506773561411],[55.79821839881462,37.380733285846055],[55.79170896641588,37.374483845289205],[55.7869817752558,37.370921871717414],[55.78326974058433,37.36976315742295],[55.77459764480862,37.36952138190073],[55.767231334883064,37.36926388983531],[55.75944126557839,37.36900421545996],[55.75317331092855,37.3690042154599],[55.74804203141267,37.3690042154599],[55.7418085514462,37.371278728704546],[55.73398529886758,37.37538548395049],[55.72603254302954,37.37944939394162],[55.71633309435157,37.38448675508207],[55.70975531473926,37.38860662812894],[55.70819247430217,37.39053781861966],[55.699577552697505,37.401888927170646],[55.693602935931466,37.40959223146138],[55.690160752534936,37.41328295106584],[55.6863182376622,37.41517122621232],[55.6827450971391,37.41663205875813],[55.68073259252698,37.418219926494935],[55.65914618665337,37.435042741436355],[55.646357966502826,37.390116656364825]]]},{"coordinates":[[[55.659219939408416,37.435272827369744],[55.62946452686264,37.470635071022045],[55.61440828362996,37.487543716651935],[55.60508021379224,37.49870170615389],[55.59730511999847,37.50831474326322],[55.59312536758997,37.521446838600134],[55.57674226078925,37.58993972800443],[55.57168495980374,37.67070640586078],[55.57275482801477,37.67937530539688],[55.59331978456364,37.73447860739884],[55.60031815246222,37.75018562339],[55.60396263926049,37.75765289328746],[55.613776765853046,37.77567733786755],[55.595385088158956,37.81450780185816],[55.55200843876584,37.726273854104264],[55.54324946764757,37.672372181740975],[55.54402812223267,37.60302098545193],[55.557262880593306,37.53641637119407],[55.57769011439758,37.47496159824484],[55.61715252098259,37.42140324863547],[55.646674635095955,37.3898175552761],[55.659219939408416,37.435272827369744]]]}]},{"key":"green","rate":600,"polygons":[{"coordinates":[[[55.78323872097888,37.36990428381343],[55.74668778494998,37.36908806702955],[55.71331468085365,37.38627418826733],[55.70914734814092,37.38953575442944],[55.69097062140305,37.413053363072024],[55.68301866448869,37.416829913365],[55.65991682084242,37.43459925746224],[55.63564864134306,37.463352538101844],[55.60743004143662,37.49656901454224],[55.598004854749675,37.507633360555985],[55.59542905982957,37.5134698473724],[55.57695612199488,37.589430006674114],[55.575497360276884,37.60573783748462],[55.57185021786885,37.67174163692306],[55.573309115645195,37.68058219783611],[55.575011094265854,37.68538871639079],[55.59129771335722,37.72847572200598],[55.60456507460934,37.75877395503821],[55.61131852022464,37.77070442073642],[55.62521042558056,37.796711119344806],[55.65147495208129,37.836193236044025],[55.6552117189009,37.83833900325595],[55.65919073912766,37.839883955648524],[55.66229603368121,37.83954063289463],[55.66569216631081,37.8387681566983],[55.69091131598713,37.829412611654384],[55.69503212438764,37.82924095027744],[55.69842540378316,37.83001342647372],[55.70147910231585,37.831472548177814],[55.716114139700124,37.838939818075296],[55.759018284147615,37.843059691122164],[55.77706647365934,37.843059691122164],[55.8215945724079,37.83765235774815],[55.828020572492676,37.831815870931734],[55.82946989885914,37.82924095027744],[55.891257317722925,37.70830551021388],[55.8934759664331,37.70135322444727],[55.89477815743256,37.6936284624844],[55.89603207765014,37.65500465266994],[55.89743063296031,37.64290252559473],[55.899407814435456,37.62968459956934],[55.90061336323242,37.62384811275293],[55.90374761403016,37.610887678792984],[55.910401026437675,37.58582511775783],[55.91093132157959,37.58204856746486],[55.91102773809568,37.57535377376369],[55.910690279236086,37.56874481075099],[55.906785183625786,37.53389755122951],[55.90543518217023,37.52737441890524],[55.9039886996854,37.52291122310445],[55.89145024871612,37.49518791072653],[55.88730201923581,37.48377242915915],[55.885758378317604,37.477249296834934],[55.88339455867481,37.4674645983486],[55.88291212874047,37.46248641841697],[55.88223671671034,37.44677940242576],[55.87741200189235,37.4309007250576],[55.87089768168177,37.41107383601949],[55.86375479538287,37.40103164546774],[55.85854158629912,37.39708343379782],[55.851879241167325,37.39365020625876],[55.847678477477196,37.391933592489224],[55.844539678283475,37.39227691524314],[55.84101426187901,37.39468017452047],[55.836962137917716,37.39639152548997],[55.83039269510333,37.3948465730974],[55.821599491113766,37.39235748313157],[55.80884096589401,37.38832344077318],[55.80294356154176,37.385233535988014],[55.795304606073955,37.37793792746748],[55.79148456396943,37.374333038551455],[55.787277246795576,37.371157303077815],[55.78323872097888,37.36990428381343]]]}]},{"key":"brown","rate":3500,"polygons":[{"coordinates":[[[55.58540824207349,37.26165077122892],[55.65789727026015,37.209208220569735],[55.72114872554261,37.198354412687564],[55.81540513407545,37.20625083602741],[55.877407997864964,37.22650687850783],[55.94200917148647,37.27388541854686],[56.007271735320394,37.50768821395701],[55.99322748525439,37.81358878768745],[55.906115227878196,38.041050840986394],[55.97412604644952,38.19758066810308],[56.03097899900607,38.06389937080084],[56.07085272708434,37.91923174537362],[56.086020406866616,37.810055109631406],[56.09197064338863,37.70087847388922],[56.10079832563578,37.482525202404844],[56.06739596131553,37.31773028052984],[56.02396784997148,37.165294977795426],[55.882197724621825,37.00873980201413],[55.75849518608422,36.98676714576416],[55.68059243881852,36.99844011939693],[55.620411563045344,37.03757891334226],[55.54189732194239,37.10479293792924],[55.58540824207349,37.26165077122892]]]},{"coordinates":[[[55.585124886540754,37.262361367728246],[55.54490909027751,37.32594886808172],[55.48578599585751,37.46945777921452],[55.46706621210719,37.63905921964422],[55.49104932620695,37.835268173501554],[55.53274111639274,37.973798904702704],[55.59694530058498,38.089155350015226],[55.666575015719324,38.13550392179253],[55.749831195862825,38.14065376310113],[55.854546956016485,38.112477881211674],[55.90607425287,38.04103456189095],[55.974027968882545,38.19766182591662],[55.92027797531286,38.267013022205596],[55.86568080133082,38.30546517064316],[55.79689064433085,38.31919808079931],[55.72759074615603,38.32125801732275],[55.58550842681638,38.27731270482272],[55.46241929904895,38.08573860814304],[55.41362217120328,37.86875862767423],[55.389005449493915,37.638045737049225],[55.41479401197214,37.402526327869545],[55.492838014287365,37.224685141346065],[55.552654013754974,37.13648089352224],[55.585124886540754,37.262361367728246]]]}]},{"key":"blue","rate":2000,"polygons":[{"coordinates":[[[55.60698913683193,37.34623437072852],[55.671890048430406,37.29707484390352],[55.733783429280294,37.26694827224817],[55.807817878017474,37.26826863096319],[55.91370896878188,37.31237803138],[55.972004143609375,37.521207813124605],[55.95891000345349,37.771318439345244],[55.876596832172865,37.968407157759444],[55.906091169374925,38.04095554719414],[55.993002038507804,37.81198072801078],[56.006469307453166,37.50573683152642],[55.941012700433895,37.27433729539356],[55.87698887094417,37.22730207810844],[55.81517864690306,37.20635939012013],[55.72111546842013,37.19949293504199],[55.6578918045135,37.20979261765918],[55.58528123100869,37.26240682969519],[55.60698913683193,37.34623437072852]]]},{"coordinates":[[[55.60684162491817,37.34639560496029],[55.570201766547804,37.38426839625057],[55.52747877913919,37.481857889048385],[55.510970747658966,37.59549772059131],[55.508584055658815,37.64665281092335],[55.51248062058692,37.69506131922409],[55.53035114776502,37.78724347864784],[55.56057127001595,37.8950468233744],[55.60816560652669,37.98817312037138],[55.66705555592235,38.03623830591825],[55.71646611235904,38.03841595794861],[55.730369016733995,38.03893094207945],[55.79526412067943,38.036098529359684],[55.83571416017445,38.01893239166434],[55.85778196797156,37.99773221161064],[55.87648990625379,37.968463946840046],[55.906014459086954,38.04105525161902],[55.85429396688921,38.11246638443143],[55.7498707214293,38.1406188502517],[55.66612949373818,38.135125686189156],[55.59640178233511,38.088090468903964],[55.53258614439255,37.97307734634542],[55.491089114620216,37.83506159927507],[55.46710602482259,37.63902430679456],[55.48602074012689,37.469079543610974],[55.54504615242163,37.32591395523206],[55.58519780785982,37.262527991792105],[55.60684162491817,37.34639560496029]]]}]},{"key":"red","rate":1500,"polygons":[{"coordinates":[[[55.62451884379385,37.4130184223862],[55.62766939132917,37.41002507712546],[55.64633678036952,37.38989778067767],[55.655291042782444,37.387408690711794],[55.70323556176535,37.34452047207757],[55.708493910227965,37.33975686886708],[55.74828406562248,37.32087411740215],[55.79812449439829,37.323930347705016],[55.829032003502206,37.34766975643278],[55.85931085725072,37.351789629479626],[55.894502056583,37.38752546809587],[55.93125141415062,37.52935918028093],[55.93394956473711,37.61218579466069],[55.92717974036209,37.71638425047112],[55.89348160431509,37.814188319990045],[55.84958172020504,37.89728915011152],[55.8765575291782,37.9682389429733],[55.95888282122756,37.77100002085408],[55.97197697059254,37.52106105601033],[55.913403893990704,37.31232082163532],[55.80759336157774,37.26837550913529],[55.73405107168916,37.267002218119664],[55.67201259852089,37.297214620463365],[55.60709367081832,37.346331231944],[55.62451884379385,37.4130184223862]]]},{"coordinates":[[[55.62443921336317,37.41310524827952],[55.61681369869353,37.42168831712718],[55.588824527874166,37.45936798936838],[55.57759406887413,37.47481751329415],[55.557166784887016,37.53627228624338],[55.54401533178241,37.60255777048633],[55.54318801049515,37.672338120217745],[55.55194699535315,37.72675477671187],[55.59547837653506,37.8149503967446],[55.595994763468745,37.815014769760914],[55.61834473689087,37.887648989884156],[55.656650022259996,37.92756026002569],[55.6681973384331,37.935113360611616],[55.682165986747414,37.937259127823495],[55.72751679381769,37.93805803923381],[55.79991114496499,37.93616976408732],[55.81402585186068,37.931706568286536],[55.84967641830661,37.89754595427286],[55.87646518782802,37.968442102954505],[55.85764258501243,37.99779619841345],[55.83571960452719,38.01891054777873],[55.79512451254463,38.03607668547394],[55.730083873705745,38.03882326750524],[55.66687478606691,38.03607668547394],[55.60803314939719,37.98766817717318],[55.56058458628602,37.89497103361843],[55.53021842679046,37.786137720630165],[55.512493953185846,37.694813868091096],[55.50869480838289,37.64640535979031],[55.51113019998819,37.5952502694583],[55.527492106599475,37.48195376066919],[55.5703123450561,37.38445009855982],[55.607061420753226,37.346341272876124],[55.62443921336317,37.41310524827952]]]}]}];

  function getZonesData(){
    if (global.KOSMOS_DELIVERY_ZONES && global.KOSMOS_DELIVERY_ZONES.length) return global.KOSMOS_DELIVERY_ZONES;
    return EMBEDDED_DELIVERY_ZONES;
  }

  var ZONES = global.KOSMOS_DELIVERY_ZONE_META || [];
  var ZONE_STYLE = global.KOSMOS_DELIVERY_ZONE_STYLE || {};
  var ZONE_HIT_ORDER = global.KOSMOS_DELIVERY_ZONE_HIT_ORDER || [];

  function pointInRing(point, ring){
    var x = point[0], y = point[1], inside = false, i, j;
    for (i = 0, j = ring.length - 1; i < ring.length; j = i++){
      var xi = ring[i][0], yi = ring[i][1];
      var xj = ring[j][0], yj = ring[j][1];
      if (((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi + 0.0) + xi)) inside = !inside;
    }
    return inside;
  }

  function findZoneKeyAt(coords, zoneData){
    var i, j, k, zd, poly, ring;
    if (!zoneData || !zoneData.length) return null;
    for (i = 0; i < ZONE_HIT_ORDER.length; i++){
      for (j = 0; j < zoneData.length; j++){
        zd = zoneData[j];
        if (zd.key !== ZONE_HIT_ORDER[i]) continue;
        for (k = 0; k < (zd.polygons || []).length; k++){
          poly = zd.polygons[k];
          ring = poly.coordinates && poly.coordinates[0];
          if (ring && pointInRing(coords, ring)) return zd.key;
        }
      }
    }
    return null;
  }

  function fmtRub(n){
    n = Math.round(+n || 0);
    return n.toLocaleString('ru-RU').replace(/\u00a0|\s/g,'\u00a0') + 'р';
  }

  function getUrlParams(){
    var p;
    try { p = new URLSearchParams(location.search); } catch(_){ return {}; }
    return {
      total  : parseInt(p.get('total'),  10) || 0,
      cake   : (p.get('cake')   || '').trim(),
      weight : (p.get('weight') || '').trim(),
      tiers  : (p.get('tiers')  || '').trim(),
      pieces : (p.get('pieces') || '').trim(),
      filling: (p.get('filling')|| '').trim(),
      tiered : p.get('tiered') === '1' || p.get('tiered') === 'true',
      ymapkey: (p.get('ymapkey') || p.get('yandexApiKey') || '').trim()
    };
  }

  function geocodeViaNominatim(query){
    var url = 'https://nominatim.openstreetmap.org/search?format=json&limit=1&q=' +
      encodeURIComponent(query + ', Москва, Россия');
    return fetch(url, {headers: {'Accept': 'application/json'}})
      .then(function(r){ return r.json(); })
      .then(function(list){
        if (!list || !list.length) return null;
        var item = list[0];
        return {
          coords: [parseFloat(item.lat), parseFloat(item.lon)],
          line: item.display_name || query
        };
      });
  }

  function resolveAddress(query, apiKey){
    apiKey = normalizeApiKey(apiKey);
    if (global.ymaps && apiKey){
      return global.ymaps.geocode(query, {
        results: 1,
        boundedBy: [[55.1, 36.8], [56.2, 38.5]],
        strictBounds: false
      }).then(function(res){
        var obj = res.geoObjects.get(0);
        if (!obj) return geocodeViaNominatim(query);
        return {
          coords: obj.geometry.getCoordinates(),
          line: obj.getAddressLine ? obj.getAddressLine() : query
        };
      }).catch(function(){ return geocodeViaNominatim(query); });
    }
    return geocodeViaNominatim(query);
  }

  function zoneMeta(key){
    if (global.Kosmos && global.Kosmos.zoneMeta) return global.Kosmos.zoneMeta(key);
    for (var i = 0; i < ZONES.length; i++){
      if (ZONES[i].key === key) return ZONES[i];
    }
    return null;
  }

  function buildTemplate(){
    return ''+
'<div class="dlv-frame">'+
'  <div class="dlv-map" data-role="map"><div class="dlv-map-canvas" data-role="map-canvas"></div></div>'+
'  <div class="dlv-address">'+
'    <input class="dlv-address-input" data-role="address" type="text" autocomplete="off" placeholder="введите адрес доставки">'+
'    <button class="dlv-address-btn" data-role="address-btn" type="button">найти</button>'+
'  </div>'+
'  <p class="dlv-title">Мы бережно доставляем торты по всей Москве и до 20 км от МКАД.</p>'+
'  <div class="dlv-zone-label">выберите зону</div>'+
'  <div class="dlv-zones kosmos-dots kosmos-dots--zones" data-role="zones"></div>'+
'  <div class="dlv-cost"><div class="lbl" data-role="delivery-lbl">стоимость доставки</div><div class="val" data-role="delivery-val">—</div></div>'+
'  <div class="dlv-total"><div class="lbl">итоговая стоимость</div>'+
'    <div class="val-row"><span class="sparkle">'+SPARKLE_SVG+'</span><div class="val" data-role="final-val">—</div><span class="sparkle">'+SPARKLE_SVG+'</span></div>'+
'  </div>'+
'  <button class="dlv-cta" data-role="cta" type="button" disabled>продолжить заказ<br>с администратором</button>'+
'</div>'+
'<div class="dlv-toast" data-role="toast"></div>';
  }

  var _ymapsQueue = [];
  var _ymapsLoading = false;

  function loadYmaps(apiKey, cb){
    if (global.ymaps){
      global.ymaps.ready(cb);
      return;
    }
    _ymapsQueue.push(cb);
    if (_ymapsLoading) return;
    _ymapsLoading = true;
    var cbName = '__kosmosYmapsReady';
    apiKey = normalizeApiKey(apiKey);
    var url = 'https://api-maps.yandex.ru/2.1/?lang=ru_RU&onload=' + cbName;
    if (apiKey) url += '&apikey=' + encodeURIComponent(apiKey);
    global[cbName] = function(){
      delete global[cbName];
      global.ymaps.ready(function(){
        var q = _ymapsQueue.slice();
        _ymapsQueue = [];
        q.forEach(function(fn){ fn(); });
      });
    };
    var s = document.createElement('script');
    s.src = url;
    s.async = true;
    s.onerror = function(){
      delete global[cbName];
      _ymapsLoading = false;
      _ymapsQueue = [];
    };
    document.head.appendChild(s);
  }

  function mountDelivery(host, options){
    if (!host) return null;
    options = options || {};
    var urlParams = getUrlParams();
    options.yandexApiKey = normalizeApiKey(
      options.yandexApiKey || urlParams.ymapkey || DEFAULT_YANDEX_API_KEY
    );

    host.innerHTML = buildTemplate();

    var $zones      = host.querySelector('[data-role="zones"]');
    var zoneStrip   = null;
    if (global.Kosmos && global.Kosmos.Dots && $zones){
      zoneStrip = global.Kosmos.Dots.mount($zones, {variant:'zones', items: ZONES});
    }
    var $mapCanvas  = host.querySelector('[data-role="map-canvas"]');
    var $address    = host.querySelector('[data-role="address"]');
    var $addressBtn = host.querySelector('[data-role="address-btn"]');
    var $deliveryL  = host.querySelector('[data-role="delivery-lbl"]');
    var $deliveryV  = host.querySelector('[data-role="delivery-val"]');
    var $finalV     = host.querySelector('[data-role="final-val"]');
    var $cta        = host.querySelector('[data-role="cta"]');
    var $toast      = host.querySelector('[data-role="toast"]');

    var mapApi = {
      map: null,
      zonePolys: {},
      placemark: null,
      activeKey: null
    };

    var state = {
      params: Object.assign({total:0,cake:'',weight:'',tiers:'',pieces:'',filling:'',tiered:false}, getUrlParams(), options.initialPayload||{}),
      rate  : null,
      name  : null,
      pickup: false,
      address: ''
    };

    function toast(msg){
      $toast.textContent = msg;
      $toast.classList.add('show');
      clearTimeout(toast._t);
      toast._t = setTimeout(function(){ $toast.classList.remove('show'); }, 3200);
    }

    function applyTieredLock(){
      var purple = zoneStrip ? zoneStrip.getButton('purple') :
        $zones.querySelector('[data-key="purple"]');
      if (!purple) return;
      if (state.params.tiered){
        if (zoneStrip) zoneStrip.setHidden('purple', true);
        else purple.classList.add('is-hidden');
        if (purple.classList.contains('is-active')){
          purple.classList.remove('is-active');
          state.rate = null; state.name = null; state.pickup = false;
          mapApi.activeKey = null;
          highlightMapZone(null);
        }
      } else {
        if (zoneStrip) zoneStrip.setHidden('purple', false);
        else purple.classList.remove('is-hidden');
        purple.removeAttribute('disabled');
        purple.removeAttribute('title');
      }
    }
    applyTieredLock();

    function render(){
      if (state.rate === null){
        $deliveryL.textContent = 'стоимость доставки';
        $deliveryV.textContent = '—';
        $finalV.textContent    = fmtRub(state.params.total);
        $cta.setAttribute('disabled','disabled');
        return;
      }
      if (state.pickup){
        $deliveryL.textContent = 'самовывоз';
        $deliveryV.textContent = 'бесплатно';
      } else {
        $deliveryL.textContent = 'стоимость доставки';
        $deliveryV.textContent = fmtRub(state.rate);
      }
      $finalV.textContent = fmtRub(state.params.total + state.rate);
      $cta.removeAttribute('disabled');
    }

    function highlightMapZone(key){
      mapApi.activeKey = key || null;
      Object.keys(mapApi.zonePolys).forEach(function(zk){
        var active = zk === key;
        mapApi.zonePolys[zk].forEach(function(poly){
          poly.options.set({
            fillOpacity: active ? 0.72 : 0.45,
            strokeWidth: active ? 5 : 3
          });
        });
      });
    }

    function selectZone(key){
      var btn = $zones.querySelector('[data-key="'+key+'"]');
      if (!btn || btn.hasAttribute('disabled') || btn.classList.contains('is-hidden')) return;
      $zones.querySelectorAll('.kosmos-dot, .dlv-zone').forEach(function(b){
        b.classList.remove('is-active');
      });
      btn.classList.add('is-active');
      state.rate   = parseInt(btn.dataset.rate, 10) || 0;
      state.name   = btn.dataset.name || '';
      state.pickup = btn.dataset.pickup === '1';
      highlightMapZone(key);
      render();
    }

    function findZoneAt(coords){
      var key = findZoneKeyAt(coords, getZonesData());
      if (key) return key;
      if (!mapApi.map || !global.ymaps) return null;
      var i, j, polys;
      for (i = 0; i < ZONE_HIT_ORDER.length; i++){
        polys = mapApi.zonePolys[ZONE_HIT_ORDER[i]] || [];
        for (j = 0; j < polys.length; j++){
          if (polys[j].geometry.contains(coords)) return ZONE_HIT_ORDER[i];
        }
      }
      return null;
    }

    function setPlacemark(coords){
      if (!mapApi.map || !global.ymaps) return;
      if (!mapApi.placemark){
        mapApi.placemark = new global.ymaps.Placemark(coords, {}, {
          preset: 'islands#redDotIcon',
          zIndex: 2000
        });
        mapApi.map.geoObjects.add(mapApi.placemark);
      } else {
        mapApi.placemark.geometry.setCoordinates(coords);
      }
    }

    function geocodeAddress(){
      var query = ($address.value || '').trim();
      if (!query){
        toast('Введите адрес');
        return;
      }
      resolveAddress(query, options.yandexApiKey)
        .then(function(hit){
          if (!hit){
            toast('Адрес не найден');
            return;
          }
          state.address = hit.line;
          $address.value = hit.line;
          if (mapApi.map){
            setPlacemark(hit.coords);
            mapApi.map.setCenter(hit.coords, 13, {duration: 300});
          }
          var key = findZoneAt(hit.coords);
          if (!key){
            toast('Адрес вне зоны доставки');
            highlightMapZone(null);
            return;
          }
          selectZone(key);
        })
        .catch(function(){
          toast('Не удалось найти адрес');
        });
    }

    var mapLoading = false;

    function refreshMapSize(){
      if (mapApi.map && mapApi.map.container && mapApi.map.container.fitToViewport){
        try { mapApi.map.container.fitToViewport(); } catch(_){}
      }
    }

    function buildMap(){
      if (mapApi.map || mapLoading || !$mapCanvas) return;
      var zoneData = getZonesData();
      if (!zoneData || !zoneData.length) return;
      mapLoading = true;

      loadYmaps(options.yandexApiKey || '', function(){
        mapLoading = false;
        if (!global.ymaps || mapApi.map) return;

        var map = new global.ymaps.Map($mapCanvas, {
          center: MAP_CENTER,
          zoom: MAP_ZOOM,
          controls: ['zoomControl']
        }, {
          suppressMapOpenBlock: true,
          yandexMapDisablePoiInteractivity: true
        });

        mapApi.map = map;
        mapApi.zonePolys = {};

        zoneData.forEach(function(zd){
          var meta = zoneMeta(zd.key);
          var style = ZONE_STYLE[zd.key] || {fill:'#ccc', stroke:'#888'};
          mapApi.zonePolys[zd.key] = [];
          (zd.polygons || []).forEach(function(poly){
            var polygon = new global.ymaps.Polygon(poly.coordinates, {
              hintContent: meta ? meta.name : zd.key,
              balloonContent: fmtRub(zd.rate)
            }, {
              fillColor: style.fill,
              fillOpacity: 0.45,
              strokeColor: style.stroke,
              strokeOpacity: 0.9,
              strokeWidth: 3,
              interactivityModel: 'default#opaque'
            });
            polygon.events.add('click', function(e){
              e.stopPropagation();
              selectZone(zd.key);
            });
            map.geoObjects.add(polygon);
            mapApi.zonePolys[zd.key].push(polygon);
          });
        });

        map.events.add('click', function(e){
          var key = findZoneAt(e.get('coords'));
          if (key) selectZone(key);
        });

        refreshMapSize();
        setTimeout(refreshMapSize, 250);
      });
    }

  function mapHasSize(){
      if (!$mapCanvas) return false;
      var r = $mapCanvas.getBoundingClientRect();
      return r.width > 20 && r.height > 20;
    }

    function ensureMap(){
      if (!mapHasSize()) return;
      if (mapApi.map) refreshMapSize();
      else buildMap();
    }

    /* карта создаётся после «далее» (панель была скрыта) или сразу, если блок уже виден */
    window.addEventListener('kosmos-next', function(){
      setTimeout(ensureMap, 60);
      setTimeout(refreshMapSize, 400);
    });
    window.addEventListener('resize', function(){ ensureMap(); });
    setTimeout(ensureMap, 120);

    $zones.addEventListener('click', function(e){
      var btn = e.target.closest('.kosmos-dot, .dlv-zone');
      if (!btn || btn.hasAttribute('disabled') || btn.classList.contains('is-hidden')) return;
      selectZone(btn.dataset.key);
    });

    if ($addressBtn) $addressBtn.addEventListener('click', geocodeAddress);
    if ($address){
      $address.addEventListener('keydown', function(e){
        if (e.key === 'Enter'){
          e.preventDefault();
          geocodeAddress();
        }
      });
    }

    function cakeParamsText(p){
      var bits = [];
      if (p.weight) bits.push(p.weight + ' кг');
      if (p.tiers) bits.push(p.tiers + ' ярусов');
      if (p.pieces) bits.push(p.pieces + ' порций');
      if (p.filling) bits.push('начинка «' + p.filling + '»');
      return bits.join(', ');
    }

    function deliveryText(){
      if (state.pickup) return 'Самовывоз';
      if (state.rate === null) return '';
      if (state.address){
        var line = 'Адрес доставки: ' + state.address;
        if (state.name) line += ' (' + state.name + ')';
        return line;
      }
      if (state.name) return 'Адрес доставки: ' + state.name;
      return '';
    }

    function buildOrderText(){
      var p = state.params;
      var cake = p.cake || 'торт';
      var params = cakeParamsText(p);
      var msg = 'Добрый день, заинтересовал торт «' + cake + '»';
      if (params) msg += ': ' + params;
      var dlv = deliveryText();
      if (dlv) msg += '. ' + dlv;
      var total = (parseInt(p.total, 10) || 0) + (state.rate === null ? 0 : (state.rate || 0));
      if (total > 0) msg += '. Итого: ' + fmtRub(total);
      return msg;
    }

    $cta.addEventListener('click', function(){
      if ($cta.hasAttribute('disabled')) return;
      var text = buildOrderText();
      var url = TELEGRAM_URL + '?text=' + encodeURIComponent(text);
      window.open(url, '_blank', 'noopener');
    });

    function setPayload(payload){
      if (!payload || typeof payload !== 'object') return;
      state.params.total   = parseInt(payload.total, 10) || 0;
      state.params.cake    = (payload.cake    || '').toString().trim();
      state.params.weight  = (payload.weight  || '').toString().trim();
      state.params.tiers   = (payload.tiers   || '').toString().trim();
      state.params.pieces  = (payload.pieces  || '').toString().trim();
      state.params.filling = (payload.filling || '').toString().trim();
      state.params.tiered  = !!payload.tiered;
      applyTieredLock();
      render();
    }

    window.addEventListener('kosmos-cake', function(e){ setPayload(e.detail); });

    try {
      var ch = new BroadcastChannel('kosmos-cake');
      ch.addEventListener('message', function(e){ setPayload(e.data); });
    } catch(_){}

    window.addEventListener('message', function(e){
      if (!e.data || typeof e.data !== 'object') return;
      if (e.data.type !== 'kosmos-cake') return;
      setPayload(e.data);
    });

    render();

    return { setPayload: setPayload, selectZone: selectZone, refreshMap: ensureMap };
  }

  global.Kosmos = global.Kosmos || {};
  global.Kosmos.mountDelivery = mountDelivery;
})(window);
