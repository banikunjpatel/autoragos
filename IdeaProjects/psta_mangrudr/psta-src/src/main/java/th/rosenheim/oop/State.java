package th.rosenheim.oop;

public enum State {
    Sunny(0),
    Cloudy(1),
    Rainy(2);

    private final int value;
    State(int value) {
        this.value = value;
    }
    public int getValue() {
        return value;
    }
}
