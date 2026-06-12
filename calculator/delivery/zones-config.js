/* Единый источник метаданных зон доставки (кнопки, карта, тарифы). */
(function(global){
  var META = [
    {key:'green',  rate:600,  name:'зелёная зона',    cls:'kosmos-dot--green',  onMap:true},
    {key:'orange', rate:1000, name:'оранжевая зона',  cls:'kosmos-dot--orange', onMap:true},
    {key:'red',    rate:1500, name:'красная зона',    cls:'kosmos-dot--red',    onMap:true},
    {key:'blue',   rate:2000, name:'голубая зона',    cls:'kosmos-dot--blue',   onMap:true},
    {key:'brown',  rate:3500, name:'коричневая зона', cls:'kosmos-dot--brown',  onMap:true},
    {key:'purple', rate:0,    name:'самовывоз',       cls:'kosmos-dot--purple', onMap:false, pickup:true}
  ];

  var STYLE = {
    green:  {fill:'#A8D8B0', stroke:'#3FA94E'},
    orange: {fill:'#F5C58A', stroke:'#E89A2E'},
    red:    {fill:'#EFA6AA', stroke:'#D2363C'},
    blue:   {fill:'#A8CFE5', stroke:'#3A9DD8'},
    brown:  {fill:'#D8C2A8', stroke:'#A98968'}
  };

  /* от центра к периферии — для клика по карте и геокодера */
  var HIT_ORDER = ['green', 'orange', 'red', 'blue', 'brown'];

  function byKey(key){
    for (var i = 0; i < META.length; i++){
      if (META[i].key === key) return META[i];
    }
    return null;
  }

  global.KOSMOS_DELIVERY_ZONE_META = META;
  global.KOSMOS_DELIVERY_ZONE_STYLE = STYLE;
  global.KOSMOS_DELIVERY_ZONE_HIT_ORDER = HIT_ORDER;
  global.Kosmos = global.Kosmos || {};
  global.Kosmos.zoneMeta = byKey;
})(window);
