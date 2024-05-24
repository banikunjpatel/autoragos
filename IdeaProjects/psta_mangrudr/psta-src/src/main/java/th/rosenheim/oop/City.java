package th.rosenheim.oop;

public abstract class City {
    private static String name;
    private final int weatherstate;
    public City(String name, int weatherstate) {
        City.name = name;
        this.weatherstate = weatherstate;
    }
    public static String getName() {
        return name;
    }
    public int getWeatherstate() {
        return weatherstate;
    }
    // this method return
    public abstract String getConnect();

    public abstract String getURL();
}
