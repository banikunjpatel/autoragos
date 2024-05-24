package th.rosenheim.oop;

import java.util.LinkedList;

public class BigCity extends City{
    private LinkedList<String> districs = getDistricts();

    private LinkedList<String> getDistricts() {
        return new LinkedList<>();
    }

    public BigCity(String districs, String name, int weatherstate) {
        super(name, weatherstate);
        this.districs = new LinkedList<>();
    }

    public String getConnect() {
        return "<p>It is" + getWeatherstate() + "in" + getName() + ".</p> <p>This also applies to" + getDistricts() + "," + getDistricts() + "," + getDistricts() + "[...] and" + getDistricts() +".</p>";
    }

    public String getURL() {
        return "weather_big_city_" + getName() + ".html";
    }
}
