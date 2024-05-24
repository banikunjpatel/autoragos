package th.rosenheim.oop;

import java.util.LinkedList;

public class WebsiteGenerator {
    private LinkedList<City> cities;
    public WebsiteGenerator() {
        cities = new LinkedList<>();
    }
    public void getNavigation(){
        StringBuffer navigation = new StringBuffer();
        for (int i = 0; i < cities.size(); i++) {
            City city = cities.get(i);
            navigation.append("<h1>The Weather App</h1><p><a href=\"" + city.getURL() + "\">" + city.getName() + "</a>|");
        }
    public void genrateWebsites(){

        }
    }
}
