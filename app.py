from flask import Flask, request, session, render_template, redirect, url_for, flash
import sqlite3
import math
import folium
import webbrowser

app = Flask(__name__)

def select_count(region, city):
    conn = sqlite3.connect("emergencyAssemblyArea.sqlite")
    cursor = conn.cursor()
    sql = "select count(name) from area where region = ? and city = ?"
    cursor.execute(sql, (region, city))
    rows = cursor.fetchone()
    cursor.close()
    conn.close()
    return rows[0]

def select_page(region, city, list_num, page):
    conn = sqlite3.connect('emergencyAssemblyArea.sqlite')
    cursor = conn.cursor()
    offset = (page-1) * list_num
    sql = 'select address, name, x, y from area where region = ? and city = ? order by address limit ? offset?'
    cursor.execute(sql, (region, city, list_num, offset))
    row = cursor.fetchall()
    cursor.close()
    conn.close()
    return row

@app.route('/')
def root() :
    return 'root'

@app.route('/main')
def main():
    session.clear()
    return render_template('main.html')

@app.route('/search')
def search():
    session.clear()
    return render_template('search.html')

@app.route('/search_proc', methods=['GET'])
def search_proc():
    if request.method == 'GET':
        region = request.args.get('region')
        city = request.args.get('city')
        if region == None or city == None:
            return redirect(url_for('search'))
        else:
            session['region'] = region
            session['city'] = city

            conn = sqlite3.connect('emergencyAssemblyArea.sqlite')
            cursor = conn.cursor()
            sql = 'select name, address, x, y from area where region = ? and city = ?'
            cursor.execute(sql,(region, city))
            row = cursor.fetchall()
            data_list = []
            for data in row:
                data_dict = {
                    'name' : data[0],
                    'address' : data[1],
                    'x' : data[2],
                    'y' : data[3]
                }
                data_list.append(data_dict)

            x_list = []
            y_list = []
            for i in range(len(data_list)):
                x = data_list[i]['x']
                y = data_list[i]['y']
                x_list.append(x)
                y_list.append(y)
            cursor.close()
            conn.close()

            count = 0
            x = x_list[0]
            y = y_list[0]

            map = folium.Map(location=(y, x), zoom_start=11)

            name_list = []
            address_list = []
            for i in range(len(x_list)):
                x = x_list[i]
                y = y_list[i]
                name = data_list[i]['name']
                address = data_list[i]['address']
                name_list.append(name)
                address_list.append(address)
                pop = name, address
                folium.Marker((y, x), popup=pop, icon=folium.Icon(color='red', icon='glyphicon glyphicon-ok')).add_to(
                    map)
                count += 1
            map.save('map.html')

            page = 1
            list_num = 20
            lists_count = select_count(region,city)
            if int(lists_count % list_num) == 0:
                page_count = int(lists_count / list_num)
            else :
                page_count = int(lists_count / list_num) + 1
            session['page_count'] = page_count
            lists = select_page(region, city, list_num, 1)
            return render_template('/result.html',region=region, city=city, data_list=data_list, page_count=page_count, lists=lists, page=page)
    else:
        return '잘못된 접근입니다.'


@app.route('/map')
def map():
    return render_template('map.html')

@app.route('/result/<int:page>')
def result(page):
    region = session.get('region')
    city = session.get('city')
    page = page
    list_num = 20
    lists_count = select_count(region, city)
    page_count = session.get('page_count')

    lists = select_page(region,city,list_num, page)

    return render_template('result.html', lists=lists, page_count=page_count, city=city, region=region, page=page)

@app.route('/zoom_proc', methods=['GET'])
def zoom_proc():
    x = request.args.get('x')
    y = request.args.get('y')
    name = request.args.get('name')
    address = request.args.get('address')
    map2 = folium.Map(location=(y, x), zoom_start=17)
    folium.Marker((y, x), popup=name, icon=folium.Icon(color='red', icon='glyphicon glyphicon-ok')).add_to(map2)
    map2.save('map2.html')
    return render_template('/zoom.html', x=x, y=y, name=name, address=address)

@app.route('/map2')
def map2():
    return render_template('map2.html')

@app.route('/zoom')
def zoom():
    return render_template('/zoom.html')




app.secret_key = 'sample_key'

if __name__ == '__main__':
    app.debug = True
    app.run()