package th.rosenheim.oop;

public class SmallCity extends City {
    public SmallCity(String name, int weatherstate){
        super(name, weatherstate);
    }

    @Override
    public String getConnect() {
        return "<p>It is" + getWeatherstate() + "in" + getName() + ".</p>";
    }

    @Override
    public String getURL() {
        return ": weather_small_city" + getName() + ".html";
    }
}
