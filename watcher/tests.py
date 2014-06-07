from bs4 import BeautifulSoup
from django.test import TestCase
from watcher.models import DraftLaw
from watcher.models import (
        crop_between,
        parse_header,
        parse_history,
        )

class UtilsTests(TestCase):

    def test_crop_between(self):
        s = 'Привет, привет!'
        self.assertEqual(crop_between(s), s)
        self.assertEqual(crop_between(s, start='и'), 'вет, привет!')
        self.assertEqual(crop_between(s, stop=' '), 'Привет,')
        self.assertEqual(crop_between(s, start=' ', stop='!'), 'привет')

    def test_parse_header(self):
        test_input = BeautifulSoup(test_input_header)
        self.assertEqual(parse_header(test_input), 
            ('413886-6',
             'О внесении изменений в Федеральный закон "Об организации и о проведении XXII Олимпийских зимних игр и XI Паралимпийских зимних игр 2014 года в городе Сочи, развитии города Сочи как горноклиматического курорта и внесении изменений в отдельные законодательные акты Российской Федерации" (в части распоряжения Олимпийскими объектами федерального значения)',
             'находится на рассмотрении')
                        )

    def test_parse_history(self):
        test_input = BeautifulSoup(test_input_history)
        self.assertEqual(parse_history(test_input), (
                [['Внесение законопроекта в Государственную Думу',
                    'направлен в Комитет Государственной Думы по вопросам собственности',
                    '23.12.2013'],
                 ['Предварительное рассмотрение законопроекта',
                    'назначить ответственный комитет',
                    '16.01.2014'],
                 ['Рассмотрение законопроекта в первом чтении',
                     'принять законопроект в первом чтении; представить поправки к законопроекту в семидневный срок со дня принятия постановления',
                     '21.05.2014']],
                 'http://asozd2.duma.gov.ru/work/dz.nsf/ByID/C66381491CE9FD9A43257CDF00531355/$File/Текст внесенный.rtf?OpenElement'))




test_input_header = '''
<div class="ecard-header">
    <h2>Законопроект № 413886-6</h2>
    <p>О внесении изменений в Федеральный закон "Об организации и о проведении XXII Олимпийских зимних игр и XI Паралимпийских зимних игр 2014 года в городе Сочи, развитии города Сочи как горноклиматического курорта и внесении изменений в отдельные законодательные акты Российской Федерации"<br />
(в части распоряжения Олимпийскими объектами федерального значения)<br />
        <span>находится на рассмотрении</span>
    </p>
</div>
                ''' #'''

test_input_history = '''
<div class="tab tab-act" id="docs">
        <ul class="alt-menu">
                <li class="hide-all"><a onclick="hideAllSections('data-block-doc'); switchClasses(this.parentNode,'alt-menu-act');" title="вернуться">Свернуть</li>
                <li class="show-all alt-menu-act"><A onclick="showAllSections('data-block-doc'); switchClasses(this.parentNode,'alt-menu-act');" title="развернуть">Развернуть</A></li>
        </ul>

        <div class="data-block data-block-doc" style="display: none">
                <table style="display: none">

                </table>
        </div>				
        <div class="data-block-show"><A onclick="Toggle(getNextElement(this.parentNode));">Регистрация писем</a></div>
        <div class="data-block-doc data-block" style="display: block">
                <table class="data-block-table nb tb-nb" style="display: none">

                </table>
                <div class="date-block-header">Регистрация писем и документов об изменении текста и паспортных данных законопроекта</div>
                <table class="data-block-table nb tb-nb">

                        <tr>
                                <td class="dbt-first-td1">дополнение состава инициаторов законопроекта (С.Б.Дорофеев)</td>
                                <td>23.12.2013</td>
                                <td></td>
                        </tr>

                        <tr>
                                <td class="dbt-first-td1">дополнение состава инициаторов законопроекта (Д.В.Волков)</td>
                                <td>17.01.2014</td>
                                <td></td>
                        </tr>

                        <tr>
                                <td class="dbt-first-td1">дополнение состава инициаторов законопроекта (А.В.Жарков)</td>
                                <td>28.02.2014</td>
                                <td></td>
                        </tr>

                        <tr>
                                <td class="dbt-first-td1">официальный отзыв Правительства Российской Федерации</td>
                                <td>29.04.2014</td>
                                <td></td>
                        </tr>

                        <tr>
                                <td class="dbt-first-td1">дополнение состава инициаторов законопроекта (А.Б.Выборный)</td>
                                <td>21.05.2014</td>
                                <td></td>
                        </tr>

                </table>
        </div>				
        <div class="data-block-show"><A onclick="Toggle(getNextElement(this.parentNode));">Внесение законопроекта в Государственную Думу</a></div>
        <div class="data-block-doc data-block" style="display: block">
                <table class="data-block-table nb tb-nb" style="display: none">

                </table>
                <div class="date-block-header">Регистрация законопроекта и материалов к нему в САДД Государственной Думы</div>
                <table class="data-block-table nb tb-nb">

                        <tr>
                                <td class="dbt-first-td1">зарегистрирован и направлен Председателю ГД</td>
                                <td>20.12.2013  16:54</td>
                                <td></td>
                        </tr>

                        <tr>
                                <td Class="dbt-first-td1"><a target=_blank title="Разместил(a): Лаптева Лидия Юрьевна/Аппарат Комитета Государственной Думы по собственности 13.01.2014 13:43" href='/work/dz.nsf/ByID/EB6BC74C5B7B3CDD43257C5F003AF0FE/$File/Письмо о включении в состав авторов.pdf?OpenElement'>Письмо депутата ГД С.Б.Дорофеева о включении его в число авторов законопроекта (Комитет Государственной Думы по вопросам собственности)</a></td>
                                <td> </td><td> </td>
                        </tr>

                        <tr>
                                <td Class="dbt-first-td1"><a target=_blank title="Разместил(a): Лаптева Лидия Юрьевна/Аппарат Комитета Государственной Думы по собственности 21.01.2014 11:17" href='/work/dz.nsf/ByID/8E5E3641FA944FA243257C67002D8B1F/$File/Письмо о включении в состав авторов.pdf?OpenElement'>Письмо депутата ГД Д.В.Волкова о включении его в число авторов законопроекта (Комитет Государственной Думы по вопросам собственности)</a></td>
                                <td> </td><td> </td>
                        </tr>

                        <tr>
                                <td Class="dbt-first-td1"><a target=_blank title="Разместил(a): Лаптева Лидия Юрьевна/Аппарат Комитета Государственной Думы по собственности 26.12.2013 12:02" href='/work/dz.nsf/ByID/F40FD195E7ABB3DF43257C4D0031AA79/$File/Текст внесенный.rtf?OpenElement'>Текст внесенного законопроекта (Комитет Государственной Думы по вопросам собственности)</a></td>
                                <td> </td><td> </td>
                        </tr>

                        <tr>
                                <td Class="dbt-first-td1"><a target=_blank title="Разместил(a): Лаптева Лидия Юрьевна/Аппарат Комитета Государственной Думы по собственности 26.12.2013 12:03" href='/work/dz.nsf/ByID/00F3E5AC06CBFA2D43257C4D0031C8F1/$File/Перечень.rtf?OpenElement'>Перечень актов федерального законодательства, подлежащих признанию утратившими силу, приостановлению, изменению, дополнению или принятию в связи с принятием данного закона (Комитет Государственной Думы по вопросам собственности)</a></td>
                                <td> </td><td> </td>
                        </tr>

                        <tr>
                                <td Class="dbt-first-td1"><a target=_blank title="Разместил(a): Лаптева Лидия Юрьевна/Аппарат Комитета Государственной Думы по собственности 26.12.2013 12:03" href='/work/dz.nsf/ByID/5711695983ADF85B43257C4D0031BD04/$File/Пояснительная записка.rtf?OpenElement'>Пояснительная записка к законопроекту (Комитет Государственной Думы по вопросам собственности)</a></td>
                                <td> </td><td> </td>
                        </tr>

                        <tr>
                                <td Class="dbt-first-td1"><a target=_blank title="Разместил(a): Лаптева Лидия Юрьевна/Аппарат Комитета Государственной Думы по собственности 26.12.2013 12:04" href='/work/dz.nsf/ByID/D97B5D29636B583843257C4D0031D799/$File/ФЭО.rtf?OpenElement'>Финансово-экономическое обоснование  (Комитет Государственной Думы по вопросам собственности)</a></td>
                                <td> </td><td> </td>
                        </tr>

                        <tr>
                                <td Class="dbt-first-td1"><a target=_blank title="Разместил(a): Лаптева Лидия Юрьевна/Аппарат Комитета Государственной Думы по собственности 26.12.2013 12:06" href='/work/dz.nsf/ByID/5D307753AA7A935943257C4D00320163/$File/Сопроводительное письмо-внесение за.pdf?OpenElement'>Сопроводительное письмо (Комитет Государственной Думы по вопросам собственности)</a></td>
                                <td> </td><td> </td>
                        </tr>

                </table>
                <div class="date-block-header">Прохождение законопроекта у Председателя Государственной Думы</div>
                <table class="data-block-table nb tb-nb">

                        <tr>
                                <td class="dbt-first-td1">направлен в Комитет Государственной Думы по вопросам собственности</td>
                                <td>23.12.2013  19:45</td>
                                <td></td>
                        </tr>

                </table>
        </div>				
        <div class="data-block-show"><A onclick="Toggle(getNextElement(this.parentNode));">Предварительное рассмотрение законопроекта, внесенного в Государственную Думу</a></div>
        <div class="data-block-doc data-block" style="display: block">
                <table class="data-block-table nb tb-nb" style="display: none">

                </table>
                <div class="date-block-header">Принятие профильным комитетом решения о представлении законопроекта в Совет Государственной Думы</div>
                <table class="data-block-table nb tb-nb">

                        <tr>
                                <td class="dbt-first-td1">предложить принять законопроект к рассмотрению (срок представления отзывов, предложений и замечаний в комитет 16.02.2014)</td>
                                <td>13.01.2014</td>
                                <td>3.9 СГ-57</td>
                        </tr>

                        <tr>
                                <td Class="dbt-first-td1"><a target=_blank title="Разместил(a): Лаптева Лидия Юрьевна/Аппарат Комитета Государственной Думы по собственности 13.01.2014 14:13" href='/work/dz.nsf/ByID/E49FE61E954C70E843257C5F003DB300/$File/Совет письмо-рассылка.doc?OpenElement'>Письмо в Совет ГД (Комитет Государственной Думы по вопросам собственности)</a></td>
                                <td> </td><td> </td>
                        </tr>

                        <tr>
                                <td Class="dbt-first-td1"><a target=_blank title="Разместил(a): Лаптева Лидия Юрьевна/Аппарат Комитета Государственной Думы по собственности 13.01.2014 14:15" href='/work/dz.nsf/ByID/C7F2D6F18A54E8FF43257C5F003DCD5C/$File/Совет-решение рассылка.doc?OpenElement'>Проект решения Совета Государственной Думы (Комитет Государственной Думы по вопросам собственности)</a></td>
                                <td> </td><td> </td>
                        </tr>

                        <tr>
                                <td Class="dbt-first-td1"><a target=_blank title="Разместил(a): Лаптева Лидия Юрьевна/Аппарат Комитета Государственной Думы по собственности 13.01.2014 14:21" href='/work/dz.nsf/ByID/BDC1F869251F2B9943257C5F003E62DF/$File/Комитет решение -рассылка.doc?OpenElement'>Решение комитета (Комитет Государственной Думы по вопросам собственности)</a></td>
                                <td> </td><td> </td>
                        </tr>

                        <tr>
                                <td Class="dbt-first-td1"><a target=_blank title="Разместил(a): Тихвинская Елена Васильевна/Правовое управление 30.12.2013 15:14" href='/work/dz.nsf/ByID/F5E535CF688634DD43257C5100433FAF/$File/1227413886-6.287.rtf?OpenElement'>Ответ Правового управления на соответствие требованиям статьи 104 Конституции РФ</a></td>
                                <td> </td><td> </td>
                        </tr>

                </table>
                <div class="date-block-header">Рассмотрение Советом Государственной Думы законопроекта, внесенного в Государственную Думу</div>
                <table class="data-block-table nb tb-nb">

                        <tr>
                                <td class="dbt-first-td1">назначить ответственный комитет (Комитет Государственной Думы по вопросам собственности); представить отзывы, предложения и замечания к законопроекту (срок представления отзывов, предложений и замечаний в комитет 16.02.2014); подготовить законопроект к рассмотрению Государственной Думой; включить законопроект в примерную программу</td>
                                <td>16.01.2014</td>
                                <td><a target=_blank href='/main.nsf/(ViewDoc)?OpenAgent&work/id.nsf/SGDProt&31514A7BC2DAA89943257C630025965B'>139, п.47</a></td>
                        </tr>

                </table>
        </div>				
        <div class="data-block-show"><A onclick="Toggle(getNextElement(this.parentNode));">Рассмотрение законопроекта в первом чтении</a></div>
        <div class="data-block-doc data-block" style="display: block">
                <table class="data-block-table nb tb-nb" style="display: none">

                </table>
                <div class="date-block-header">Принятие ответственным комитетом решения о представлении законопроекта в Совет Государственной Думы</div>
                <table class="data-block-table nb tb-nb">

                        <tr>
                                <td class="dbt-first-td1">предложить принять законопроект в первом чтении (предлагаемая дата рассмотрения ГД 21.05.2014)</td>
                                <td>14.05.2014</td>
                                <td>60</td>
                        </tr>

                        <tr>
                                <td Class="dbt-first-td1"><a target=_blank title="Разместил(a): Орлов Марат Шамильевич/Аппарат комитета Государственной Думы по физической культуре, спорту и делам молодежи 04.03.2014 15:45" href='/work/dz.nsf/ByID/4BB337A020C5005943257C910046172F/$File/Заключение Комитета.rtf?OpenElement'>Заключение комитета-соисполнителя (Комитет Государственной Думы по физической культуре, спорту и делам молодежи)</a></td>
                                <td> </td><td> </td>
                        </tr>

                        <tr>
                                <td Class="dbt-first-td1"><a target=_blank title="Разместил(a): Лаптева Лидия Юрьевна/Аппарат Комитета Государственной Думы по собственности 05.05.2014 14:53" href='/work/dz.nsf/ByID/117EC2161FCDAEF643257CCF00415B4A/$File/Отзыв Правительства.doc?OpenElement'>Официальный отзыв Правительства Российской Федерации (Комитет Государственной Думы по вопросам собственности)</a></td>
                                <td> </td><td> </td>
                        </tr>

                        <tr>
                                <td Class="dbt-first-td1"><a target=_blank title="Разместил(a): Лаптева Лидия Юрьевна/Аппарат Комитета Государственной Думы по собственности 11.03.2014 10:22" href='/work/dz.nsf/ByID/2E4A102BE544686243257C9800288301/$File/Письмо о включении с состав авторов.pdf?OpenElement'>Письмо депутата ГД А.В.Жаркова о включении его в число авторов законопроекта (Комитет Государственной Думы по вопросам собственности)</a></td>
                                <td> </td><td> </td>
                        </tr>

                        <tr>
                                <td Class="dbt-first-td1"><a target=_blank title="Разместил(a): Соловьева Татьяна Григорьевна/отдел законодательной техники и систематизации законодательства 14.02.2014 14:29" href='/work/dz.nsf/ByID/BBC0893C9CB563E943257C7F003F14C1/$File/0128413886-6.287.rtf?OpenElement'>Заключение Правового управления</a></td>
                                <td> </td><td> </td>
                        </tr>

                        <tr>
                                <td Class="dbt-first-td1"><a target=_blank title="Разместил(a): Лаптева Лидия Юрьевна/Аппарат Комитета Государственной Думы по собственности 14.05.2014 14:46" href='/work/dz.nsf/ByID/720EF3BA68586F4343257CD80040A599/$File/Совет-решение первое.doc?OpenElement'>Проект решения Совета Государственной Думы (Комитет Государственной Думы по вопросам собственности)</a></td>
                                <td> </td><td> </td>
                        </tr>

                        <tr>
                                <td Class="dbt-first-td1"><a target=_blank title="Разместил(a): Лаптева Лидия Юрьевна/Аппарат Комитета Государственной Думы по собственности 14.05.2014 14:47" href='/work/dz.nsf/ByID/BAAC2A0246EE11F243257CD80040BBAD/$File/Постановление-первое проект (7дневн.doc?OpenElement'>Проект постановления Государственной Думы (Комитет Государственной Думы по вопросам собственности)</a></td>
                                <td> </td><td> </td>
                        </tr>

                        <tr>
                                <td Class="dbt-first-td1"><a target=_blank title="Разместил(a): Лаптева Лидия Юрьевна/Аппарат Комитета Государственной Думы по собственности 14.05.2014 14:48" href='/work/dz.nsf/ByID/64FE32F1FA5A66B443257CD80040E548/$File/Текст внесенный.rtf?OpenElement'>Текст законопроекта к первому чтению (Комитет Государственной Думы по вопросам собственности)</a></td>
                                <td> </td><td> </td>
                        </tr>

                        <tr>
                                <td Class="dbt-first-td1"><a target=_blank title="Разместил(a): Лаптева Лидия Юрьевна/Аппарат Комитета Государственной Думы по собственности 14.05.2014 14:49" href='/work/dz.nsf/ByID/95D58E5BB6ECAC8D43257CD80040F6E1/$File/Совет-письмо первое.doc?OpenElement'>Письмо в Совет ГД (Комитет Государственной Думы по вопросам собственности)</a></td>
                                <td> </td><td> </td>
                        </tr>

                        <tr>
                                <td Class="dbt-first-td1"><a target=_blank title="Разместил(a): Лаптева Лидия Юрьевна/Аппарат Комитета Государственной Думы по собственности 14.05.2014 14:52" href='/work/dz.nsf/ByID/64F8E157B75BD46043257CD800413B80/$File/Комитет-решение первое.doc?OpenElement'>Решение комитета (Комитет Государственной Думы по вопросам собственности)</a></td>
                                <td> </td><td> </td>
                        </tr>

                        <tr>
                                <td Class="dbt-first-td1"><a target=_blank title="Разместил(a): Лаптева Лидия Юрьевна/Аппарат Комитета Государственной Думы по собственности 14.05.2014 14:53" href='/work/dz.nsf/ByID/825B30273607C7E543257CD800414B28/$File/zakl_RZD_obmen.doc?OpenElement'>Заключение ответственного комитета (Комитет Государственной Думы по вопросам собственности)</a></td>
                                <td> </td><td> </td>
                        </tr>

                        <tr>
                                <td Class="dbt-first-td1"><a target=_blank title="Разместил(a): Лаптева Лидия Юрьевна/Аппарат Комитета Государственной Думы по собственности 26.02.2014 16:54" href='/work/dz.nsf/ByID/B690EF5E358CE9EA43257C8B004C6F9E/$File/Заключение Счетной палаты.pdf?OpenElement'>Заключение Счетной палаты Российской Федерации (Комитет Государственной Думы по вопросам собственности)</a></td>
                                <td> </td><td> </td>
                        </tr>

                </table>
                <div class="date-block-header">Рассмотрение Советом Государственной Думы законопроекта, представленного ответственным комитетом</div>
                <table class="data-block-table nb tb-nb">

                        <tr>
                                <td class="dbt-first-td1">назначить комитет-соисполнитель (Комитет Государственной Думы по физической культуре, спорту и делам молодежи)</td>
                                <td>24.02.2014</td>
                                <td><a target=_blank href='/main.nsf/(ViewDoc)?OpenAgent&work/id.nsf/SGDProt&4AF21029F9B2CBE543257C8D00269473'>148, п.134</a></td>
                        </tr>

                        <tr>
                                <td class="dbt-first-td1">внести законопроект на рассмотрение Государственной Думы</td>
                                <td>19.05.2014</td>
                                <td><a target=_blank href='/main.nsf/(ViewDoc)?OpenAgent&work/id.nsf/SGDProt&826B21D90EF571BB43257CDE0028CCF3'>169, п.54</a></td>
                        </tr>

                </table>
                <div class="date-block-header">Рассмотрение законопроекта Государственной Думой</div>
                <table class="data-block-table nb tb-nb">

                        <tr>
                                <td class="dbt-first-td1">принять законопроект в первом чтении; представить поправки к законопроекту в семидневный срок со дня принятия постановления</td>
                                <td>21.05.2014</td>
                                <td>4366-6 ГД</td>
                        </tr>

                        <tr>
                                <td Class="dbt-first-td1"><a target=_blank title="Разместил(a): Лаптева Лидия Юрьевна/Аппарат Комитета Государственной Думы по собственности 21.05.2014 18:04" href='/work/dz.nsf/ByID/013831CD0ADB37AA43257CDF0052D06F/$File/Постановление-первое проект (7дневн.doc?OpenElement'>Постановление Государственной Думы (Комитет Государственной Думы по вопросам собственности)</a></td>
                                <td> </td><td> </td>
                        </tr>

                        <tr>
                                <td Class="dbt-first-td1"><a target=_blank title="Разместил(a): Лаптева Лидия Юрьевна/Аппарат Комитета Государственной Думы по собственности 21.05.2014 18:07" href='/work/dz.nsf/ByID/C66381491CE9FD9A43257CDF00531355/$File/Текст внесенный.rtf?OpenElement'>Текст законопроекта, принятого в первом чтении (Комитет Государственной Думы по вопросам собственности)</a></td>
                                <td> </td><td> </td>
                        </tr>

                </table>
        </div>				
        <div class="data-block-show"><A onclick="Toggle(getNextElement(this.parentNode));">Рассмотрение законопроекта во втором чтении</a></div>
        <div class="data-block-doc data-block" style="display: block">
                <table class="data-block-table nb tb-nb" style="display: none">

                </table>
                <div class="date-block-header">Принятие ответственным комитетом решения о представлении законопроекта в Совет Государственной Думы</div>
                <table class="data-block-table nb tb-nb">

                        <tr>
                                <td Class="dbt-first-td1">- - - - - - - - - - - - - - Дата события не определена - - - - - - - - - - - - - -</td>
                                <td> </td><td> </td>
                        </tr>

                <tr>
                        <td Class="dbt-first-td1"> <a target=_blank title="Разместил(a): Соловьева Татьяна Григорьевна/отдел законодательной техники и систематизации законодательства 30.05.2014 09:32" href='/work/dz.nsf/ByID/882ED184DFAC31EF43257CE80023EEB9/$File/0528413886-6.287.rtf?OpenElement'>Заключение Правового управления</a> </td>
                        <td> </td><td> </td>
                </tr>

                </table>
        </div>	

</div>
                                '''
